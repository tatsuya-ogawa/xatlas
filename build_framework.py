# -*- coding: utf-8 -*-

import os
import sys
import shutil
import glob

framework_name = "xatlas"


def build(srcroot, buildroot, target, arch):
    builddir = os.path.join(buildroot, target + '-' + arch)
    if os.path.isdir(builddir):
        shutil.rmtree(builddir)

    os.makedirs(builddir)
    currdir = os.getcwd()
    os.chdir(builddir)
    cmakeargs = ("-DARCH=%s " +
                 "-DPLATFORM=%s ") % (arch, target)
    os.system("cmake %s %s" % (cmakeargs, srcroot))
    os.system("make VERBOSE=1")
    os.chdir(currdir)


def build_framework(srcroot, dstroot):
    targets = ["iPhoneOS", "iPhoneSimulator"]
    archs = ["arm64",  "i386"]
    for i in range(len(targets)):
        build(srcroot, os.path.join(dstroot, "build"), targets[i], archs[i])
    put_framework_together(srcroot, dstroot)


def put_framework_together(srcroot, dstroot):
    targetlist = glob.glob(os.path.join(dstroot, "build", "*"))
    targetlist = [os.path.basename(t) for t in targetlist]

    # set the current dir to the dst root
    currdir = os.getcwd()
    framework_dir = dstroot + f"/{framework_name}.framework"
    if os.path.isdir(framework_dir):
        shutil.rmtree(framework_dir)
    os.makedirs(framework_dir)
    os.chdir(framework_dir)

    dstdir = "Versions/A"
    os.makedirs(dstdir + "/Resources")

    # copy headers
    # shutil.copytree(f"../../{framework_name}", dstdir + "/Headers")

    # make universal lib
    wlist = " ".join(
        ["../build/" + t + f"/lib{framework_name}.a" for t in targetlist])
    os.system("lipo -create " + wlist + " -o " + dstdir + f"/{framework_name}")

    # make symbolic links
    os.symlink("A", "Versions/Current")
    os.symlink("Versions/Current/Headers", "Headers")
    os.symlink("Versions/Current/Resources", "Resources")
    os.symlink(f"Versions/Current/{framework_name}", framework_name)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:\n\t./build_framework.py <outputdir>\n\n")
        sys.exit(0)

    build_framework(os.path.abspath(os.path.dirname(sys.argv[0])),
                    os.path.abspath(sys.argv[1]))
