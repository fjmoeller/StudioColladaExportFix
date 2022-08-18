# StudioColladaExportFix
a small program to remove the LEGO logo and fix the collada export files that are being exported by Bricklinks Studio
still very much WIP, a lot of code can go away and some things aren't fixed yet

## The Problem
1. A matrix that is bound to a submodel does not move the parts and submodels within that submodel
2. Colors dont get exported correctly

## Solution
1. Split up all linked submodels into non linked ones and then add the parent matrix to each child
2. The material of the lego logos make the other materials not work -> i just remove those materials (as they get exported even if you didnt check the export logos checkbox)

# Example
py remover.py {dae file to edit}

# Disclaimers
1. The dae file you put into this script gets overwritten by the corrected one
2. You will need to export your model WITHOUT the lego logos, I might fix that in the future

# Dependencies
This script uses numpy https://numpy.org/install/ and Python 3.9.7
