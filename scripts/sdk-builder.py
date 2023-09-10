import os
import random
import string
import subprocess
import sys
import json
from typing import Literal
import pydantic
import threading

from hyko_sdk.metadata import MetaData, MetaDataBase, IOPortType, Property
from hyko_sdk.utils import metadata_to_docker_label

skip_folders = ["__pycache__", "venv"]
all_built_functions: list[str]  = []
threads: list[threading.Thread] = []

class FunctionBuildError(RuntimeError):
    category: str
    function_name: str
    version: str
    reason: str
    def __init__(self,  category: str, function_name:str, version: str, reason: str) -> None:
        self.category = category
        self.function_name = function_name
        self.version = version
        self.reason = reason
        super().__init__(f"Error while building {function_name + ':' + version}. Reason: {reason}")


class NotAllowedTypes(FunctionBuildError):
    def __init__(self, category:str, function_name: str, version: str, field_name: str, field_type: Literal["input"] | Literal["output"] | Literal["param"]) -> None:
        super().__init__(category, function_name, version, f"Dictionnary or None types are not allowed: {field_type} name: {field_name}")

class UnionNotAllowed(FunctionBuildError):
    def __init__(self, category:str, function_name: str, version: str, field_name: str, field_type: Literal["input"] | Literal["output"] | Literal["param"]) -> None:
        super().__init__(category, function_name, version, f"Union is not allowed in {field_type} ports: {field_type} name: {field_name}")

class EnumNotAllowed(FunctionBuildError):
    def __init__(self, category:str, function_name: str, version: str, field_name: str, field_type: Literal["input"] | Literal["output"] | Literal["param"]) -> None:
        super().__init__(category, function_name, version, f"Enum is not allowed in {field_type} ports: {field_type} name: {field_name}")

class UnknownArrayItemsType(FunctionBuildError):
    def __init__(self, category:str, function_name: str, version: str, field_name: str, field_type: Literal["input"] | Literal["output"] | Literal["param"]) -> None:
        super().__init__(category, function_name, version, f"list[Unknown] is not allowed. {field_type} name: {field_name}")


failed_functions: list[FunctionBuildError] = []
failed_functions_lock = threading.Lock()



def process_function_dir(path: str, registry_host: str, push_image: bool):
    """Path has to be a valid path with no spaces in it """
    if path[:2] == './':
        path = path[2:]
    
    if path[-1] == '/':
        path = path[:-1]
    
    splitted = path.split("/")
    try:
        if len(splitted) == 2:
            version = splitted[0]
            function_name = splitted[1]
            category = "uncategorized"
        elif len(splitted) > 2:
            version = splitted[-1]
            function_name = splitted[-2]
            category = "/".join(splitted[:-2]).lower()
        else:
            raise FunctionBuildError(path, "unknown", path, "Make sure your function follows the correct folder structure: catgeory/fn_name/v1/")
        
        print(f"Processing function: {category=} {function_name=} {version=}")


        print("Building metadata...")
        metadata_tag = f"{registry_host}/{category.lower()}/{function_name.lower()}:metadata-{version}"
        try:
            subprocess.run(f"docker build -t {metadata_tag} ./{path}".split(' '), check=True)
        except subprocess.CalledProcessError:
            raise FunctionBuildError(category, function_name, version, "Error while running metadata docker container")

        __METADATA__START__SPECIAL__TOKEN__ = "__METADATA__START__SPECIAL__TOKEN__" + ''.join(random.choice(string.ascii_letters) for _ in range(16))
        try:
            metadata_process = subprocess.run(f'docker run -it --rm {metadata_tag} python -c'.split(' ') + [f"from main import func;print('{__METADATA__START__SPECIAL__TOKEN__}');print(func.dump_metadata())"], capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            print(e.stdout.decode())
            raise FunctionBuildError(category, function_name, version, "Error while running metadata docker container")
        
        splitted = metadata_process.stdout.decode().split(__METADATA__START__SPECIAL__TOKEN__)
        if len(splitted) == 2:
            metadata = splitted[1]
        elif len(splitted) == 1:
            metadata = splitted[0]
        else:
            print("Probably an error happen in while catching stdout from metadata")
            return
        
        print("METADATA:", metadata)
        try:
            metadata = MetaDataBase(**json.loads(metadata))
            metadata = MetaData(**metadata.model_dump(exclude_unset=True, exclude_none=True, by_alias=True), name=function_name, version=version, category=category)
        except pydantic.ValidationError:
            raise FunctionBuildError(category, function_name, version, "Invalid Function MetaData")
        
        subprocess.run(f"docker rmi -f {metadata_tag}:latest".split(' '))
        
        print("Type checking and validating schema...")
        
        fields: list[str] = []
        
        def check_property(
            field: Property, 
            field_name: str, 
            field_type: Literal["input", "output", "param"], 
            allow_union: bool, 
            allow_enum: bool
        ):
            if field.type == IOPortType.OBJECT or field.type == IOPortType.NULL:
                raise NotAllowedTypes(category, function_name, version, field_name, field_type) 

            if not allow_union:
                if field.anyOf is not None:
                    if len(field.anyOf) == 2 and (
                            field.anyOf[0].type is not None and
                            field.anyOf[0].type == IOPortType.NULL or
                            field.anyOf[1].type is not None and
                            field.anyOf[1].type == IOPortType.NULL
                        ):
                        """This is to allow Optional[Type]"""
                        pass
                    else:
                        raise UnionNotAllowed(category, function_name, version, field_name, field_type)

            if not allow_enum:
                if field.ref is not None:
                    raise EnumNotAllowed(category, function_name, version, field_name, field_type)
                
            if field.type == IOPortType.ARRAY:
                if field.items is not None:
                    check_property(field.items, field_name, field_type, allow_union, allow_enum)
                            
                elif field.prefixItems is not None:
                    for item in field.prefixItems:
                        check_property(item, field_name, field_type, allow_union, allow_enum)
                else:
                    raise UnknownArrayItemsType(category, function_name, version, field_name, field_type)
                
        # INPUTS
        for field_name, field in metadata.inputs.properties.items():
            check_property(field, field_name, "input", allow_union=True, allow_enum=True)
            fields.append(field_name)

        
        # PARAMETERS
        for field_name, field in metadata.params.properties.items():
            check_property(field, field_name, "param", allow_union=False, allow_enum=True)
            fields.append(field_name)
            
            
        # OUTPUTS
        for field_name, field in metadata.outputs.properties.items():
            check_property(field, field_name, "output", allow_union=False, allow_enum=False)
            fields.append(field_name)
        
        unique_fields = set(fields)
        if len(unique_fields) != len(fields):
            raise FunctionBuildError(category, function_name, version, "Port name must be unique within a function (across inputs, params and outputs)")
        
        print("Building...")
        function_tag = f"{registry_host}/{category.lower()}/{function_name.lower()}:{version}"
        build_cmd = f"docker build "
        build_cmd += f"--build-arg CATEGORY={category} "
        build_cmd += f"--build-arg FUNCTION_NAME={function_name} "
        build_cmd += f"-t {function_tag} "
        build_cmd += f"""--label metadata="{metadata_to_docker_label(metadata)}" """
        build_cmd += f"./{path}"
        print("Executing cmd: ", build_cmd.split(' '))
        try:
            subprocess.run(["/bin/sh", "-c", build_cmd], check=True)
        except subprocess.CalledProcessError:
            raise FunctionBuildError(category, function_name, version, "Failed to build function main docker image")
        
        if push_image:
            print()
            print("Pushing...")
            try:
                subprocess.run(f"docker push {function_tag}".split(' '), check=True)
            except subprocess.CalledProcessError:
                raise FunctionBuildError(category, function_name, version, f"Failed to push to docker registry {registry_host}")
            
    except FunctionBuildError as e:
        failed_functions_lock.acquire()
        failed_functions.append(e)
        failed_functions_lock.release()
    # except Exception as e:
    #     failed_functions_lock.acquire()
    #     failed_functions.append(FunctionBuildError(path, "unknown", "Unexpected: " + str(e)))
    #     failed_functions_lock.release()
    

def walk_directory(path: str, no_gpu: bool, threaded: bool, registry_host: str, push_image: bool):

    print("Walking:", path)
    
    ls = os.listdir(path)
    
    if "main.py" in ls and "Dockerfile" in ls:
        if no_gpu:
            with open(path + '/Dockerfile') as f:
                dockerfile = f.read()
                if 'cuda' in dockerfile:
                    return
                
        all_built_functions.append(path)
                
        if threaded:
            thread = threading.Thread(target=process_function_dir, args=[path, registry_host, push_image])
            thread.start()
            threads.append(thread)
        else:
            process_function_dir(path, registry_host, push_image)
            
    else:
        for sub_folder in ls:

            if sub_folder in skip_folders:
                continue
            
            if not os.path.isdir(path + '/' + sub_folder):
                continue
            
            walk_directory(path + '/' + sub_folder, no_gpu, threaded, registry_host, push_image)


if __name__ == "__main__":
    directory = "./sdk"
    threaded = False
    no_gpu = True
    registry_host = "registry.traefik.me"
    skip_next_arg = False
    push_image = True
    for i, arg in enumerate(sys.argv):
        if i == 0:
            continue
        
        if skip_next_arg:
            skip_next_arg = False
            continue
        
        if arg[:2] == "--":
            if arg == "--threaded":
                threaded = True
            elif arg == "--cuda":
                no_gpu = False
            elif arg == "--dir":
                skip_next_arg = True
                if i + 1 >= len(sys.argv):
                    print("No directory was provided after --dir")
                    exit(1)
                directory = sys.argv[i + 1]
            elif arg == "--registry":
                skip_next_arg = True
                if i + 1 >= len(sys.argv):
                    print("No registry host was provided after --registry")
                    exit(1)
                registry_host = sys.argv[i + 1]
            elif arg == '--no-push':
                push_image = False
            else:
                print(f"unknown argument: {arg}")
                exit(1)
        else:
            print(f"unknown argument: {arg}")
            exit(1)
                
    build_info = f"Building {directory}"  
    if threaded:
        build_info += " with multithreading"
    if no_gpu:
        build_info += ". Skipping Dockerfiles with torch-cuda as base image"
    if push_image: 
        build_info += f". Pushing to {registry_host}"
        
    print(build_info)
    
    if not no_gpu:
        subprocess.run(f"docker build -t torch-cuda:latest -f common_dockerfiles/torch-cuda.Dockerfile .".split(" "))
        
    subprocess.run(f"docker build -t hyko-sdk:latest -f common_dockerfiles/hyko-sdk.Dockerfile .".split(" "))
    
    
    if directory[-1] == '/':
        directory = directory[:-1]
    walk_directory(directory, no_gpu, threaded, registry_host, push_image)
    
    if (threaded):
        for thread in threads:
            thread.join()
        
        
    successful_count = len(all_built_functions) - len(failed_functions)
    print(f"Successfully built: {successful_count} function. Failed to build: {len(failed_functions)} function")
    for fn in failed_functions:
        print(f"ERROR WHILE BUILDING: {fn.category}/{fn.function_name}:{fn.version} REASON: {fn.reason}")
    