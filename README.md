# odoo_order_file
An automatic orderer for odoo files


## Commands

To reorder a file:`py odoo_order_file.py <file_name1 | dir_name1> <file_name2 | dir_name2> ...`<br>
To reorder a directory: `py odoo_order_file.py <dir_name1>`<br><br>


To reorder multiple file: `py odoo_order_file.py <file_name1> <file_name2>  <file_name2>...`<br>
To reorder multiple directory: `py odoo_order_file.py <dir_name1> <dir_name2>...`<br><br>

To reorder file/directory: `py odoo_order_file.py <file_name1 | dir_name1> <file_name2 | dir_name2> ...`<br>


> [!WARNING]
> The method that scan the directory is recursive so if a directory contain a symbolic link to himself it's going to crash
