import subprocess
import os
import torch 
from packaging.version import parse, Version
from pathlib import Path
from setuptools import setup, find_packages
from torch.utils.cpp_extension import (
    BuildExtension,
    CUDAExtension,
    CUDA_HOME,
)
from pathlib import Path
from pyffpa import __version__

# ninja build does not work unless include_dirs are abs path
this_dir = os.path.dirname(os.path.abspath(__file__))


def get_long_description():
    description = (Path(this_dir) / "README.md").read_text(encoding="utf-8")
    # replace relative repository path to absolute link to the release
    static_url = f"https://github.com/DefTruth/faster-prefill-attention/blob/main"
    description = description.replace("docs/", f"{static_url}/docs/")
    return description


def get_device_name():
    device_name = torch.cuda.get_device_name(torch.cuda.current_device())
    # since we will run GPU on WSL2, so add WSL2 tag.
    if "Laptop" in device_name:
        device_name += " WSL2"
    return device_name


def get_device_capability():
    return torch.cuda.get_device_capability(torch.cuda.current_device())


def get_build_sources():
    build_sources = []
    build_sources.append(f'{this_dir}/csrc/cuda/faster_prefill_attn_F16F16F16F16_L1.cu')
    build_sources.append(f'{this_dir}/csrc/cuda/faster_prefill_attn_F32F16F16F32_L1.cu')
    build_sources.append(f'{this_dir}/csrc/pybind/faster_prefill_attn_api.cc')
    return build_sources


def get_build_cuda_cflags(build_pkg: bool = False):
    extra_cuda_cflags = []
    extra_cuda_cflags.append("-O3")
    extra_cuda_cflags.append("-std=c++17")
    extra_cuda_cflags.append("-U__CUDA_NO_HALF_OPERATORS__")
    extra_cuda_cflags.append("-U__CUDA_NO_HALF_CONVERSIONS__")
    extra_cuda_cflags.append("-U__CUDA_NO_HALF2_OPERATORS__")
    extra_cuda_cflags.append("-U__CUDA_NO_BFLOAT16_CONVERSIONS__")
    extra_cuda_cflags.append("--expt-relaxed-constexpr")
    extra_cuda_cflags.append("--expt-extended-lambda")
    extra_cuda_cflags.append("--use_fast_math")
    extra_cuda_cflags.append("-diag-suppress 177" if not build_pkg else "--ptxas-options=-v")
    extra_cuda_cflags.append("-Xptxas -v" if not build_pkg else "--ptxas-options=-O3")
    extra_cuda_cflags.append(f'-I {this_dir}/include')
    return extra_cuda_cflags


# package name managed by pip, which can be remove by `pip uninstall pyffpa -y`
PACKAGE_NAME = "pyffpa"

ext_modules = []
generator_flag = []
cc_flag = []
cc_flag.append("-gencode")
cc_flag.append("arch=compute_80,code=sm_80")
cc_flag.append("-gencode")
cc_flag.append("arch=compute_89,code=sm_89")


# helper function to get cuda version
def get_cuda_bare_metal_version(cuda_dir):
    raw_output = subprocess.check_output([cuda_dir + "/bin/nvcc", "-V"], universal_newlines=True)
    output = raw_output.split()
    release_idx = output.index("release") + 1
    bare_metal_version = parse(output[release_idx].split(",")[0])

    return raw_output, bare_metal_version


if CUDA_HOME is not None:
    _, bare_metal_version = get_cuda_bare_metal_version(CUDA_HOME)
    if bare_metal_version >= Version("11.8"):
        cc_flag.append("-gencode")
        cc_flag.append("arch=compute_90,code=sm_90")


# cuda module
# may need export LD_LIBRARY_PATH=PATH-TO/torch/lib:$LD_LIBRARY_PATH
ext_modules.append(
    CUDAExtension(
        # package name for import
        name="pyffpa_cuda",
        sources=get_build_sources(),
        extra_compile_args={
            # add c compile flags
            "cxx": ["-O3", "-std=c++17"] + generator_flag,
            # add nvcc compile flags
            "nvcc": get_build_cuda_cflags(build_pkg=True) + generator_flag + cc_flag,
        },
        include_dirs=[
            Path(this_dir) / "include" ,
        ],
    )
)

def fetch_requirements():
    with open("requirements.txt") as f:
        reqs = f.read().strip().split("\n")
    return reqs

setup(
    name=PACKAGE_NAME,
    version=__version__,
    author="DefTruth",
    author_email="qyjdef@163.com",
    packages=find_packages(
        exclude=(
            "build",
            "dist",
            "include",
            "csrc",
            "tests",
            "bench",
            "tmp",
            "pyffpa.egg-info",
        )
    ),
    description="FFPA: Yet another Faster Flash Prefill Attention for large headdim, ~1.5x faster than SDPA EA.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/DefTruth/faster-prefill-attention",
    ext_modules=ext_modules,
    cmdclass={ "build_ext": BuildExtension},
    python_requires=">=3.10",
    install_requires=fetch_requirements(),
    extras_require={
        # optional dependencies, required by some features
        "all": [],
        # dev dependencies. Install them by `pip3 install 'akvattn[dev]'`
        "dev": [
            "pre-commit",
            "packaging",
            "ninja",
        ],
    },
)



