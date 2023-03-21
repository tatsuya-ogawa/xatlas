# -*- coding: utf-8 -*-

import os
import sys
import shutil
import glob

framework_name = "xatlas"
project_root_dir = os.path.dirname(__file__)

def build(srcroot, buildroot, target):
    builddir = os.path.join(buildroot, target)
    if os.path.isdir(builddir):
        shutil.rmtree(builddir)

    os.makedirs(builddir)
    currdir = os.getcwd()
    os.chdir(builddir)
    cmakeargs = f"-G Xcode -DCMAKE_TOOLCHAIN_FILE=ios.toolchain.cmake -DPLATFORM={target}"
    os.system("cmake %s %s" % (cmakeargs, srcroot))
    os.system("cmake --build . --config Release")
    os.chdir(currdir)

def build_framework(srcroot, dstroot):
    targets = ["OS","SIMULATOR"]
    for i in range(len(targets)):
        build(srcroot, os.path.join(dstroot, "build"), targets[i])
        builddir = os.path.join(dstroot,"build",targets[i])
    put_xcframework_together(dstroot)

def put_xcframework_together(dstroot):
    os.makedirs(f"{dstroot}/headers",exist_ok=True)
    headers =  glob.glob(f"{project_root_dir}/source/{framework_name}/*.h",recursive=True)
    for h in headers:
        shutil.copy(h , f"{dstroot}/headers" )
    libs = glob.glob(f"{dstroot}/**/lib{framework_name}.a",recursive=True)
    libs = [f"-library {l} -headers {dstroot}/headers" for l in libs]

    os.system(f"xcodebuild -create-xcframework "+" ".join(libs) + f" -output {dstroot}/{framework_name}.xcframework")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:\n\t./build_framework.py <outputdir>\n\n")
        sys.exit(0)

    build_framework(os.path.abspath(os.path.dirname(sys.argv[0])),
                    os.path.abspath(sys.argv[1]))
