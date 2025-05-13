from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import os
import subprocess

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        cmake_args = [
            '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
            '-DPYTHON_EXECUTABLE=' + sys.executable,
            '-DOpenGL_GL_PREFERENCE=GLVND'  # Added to fix OpenGL preference warning
        ]

        build_args = ['--', '-j4']

        env = os.environ.copy()
        
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
            
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, 
                              cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, 
                              cwd=self.build_temp)

setup(
    name='heat_model_viewer',
    version='0.1',
    author='Your Name',
    description='OpenGL viewer for heat model',
    ext_modules=[CMakeExtension('heat_model_viewer')],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
)