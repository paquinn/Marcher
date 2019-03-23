# Report
This link should be viable from anywhere without an account.

https://www.notion.so/CSE-501-Final-Report-75f0094d01c342048f8140bdc0b55950

# Marcher language
Basic DSL to support creating scenes for a ray marching renderer.

# Install
Copy the `march.py` file into your directors and add
 
 `from marcher import *` to your python file. Everything else should then work automatically
 
 Define some Objects make a camera and view your creations.
 
 Use `Camera().view({object})` to tell the compiler which Object to render.
 
 To save a compiled program use `Camera().save({object}, {file})`
  
 Examples can be found at `/examples` 
 
 