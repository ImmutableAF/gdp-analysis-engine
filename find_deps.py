import ast
import os

# Define your internal packages to exclude from the "external" list
INTERNAL_PACKAGES = {
    'config_core', 'loading_core', 'pipeline', 
    'ui', 'utils', 'main', 'tests'
}

def get_imports_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imports.add(node.module.split('.')[0])
    return imports

def main():
    root_dir = os.getcwd()
    all_external_deps = set()
    
    # Standard library modules to ignore (partial list)
    stdlib = {'os', 'sys', 'ast', 'json', 'logging', 'datetime', 're', 'pathlib', 'math'}

    for root, dirs, files in os.walk(root_dir):
        # Skip the virtual environment and git folders
        if '.venv' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                deps = get_imports_from_file(full_path)
                all_external_deps.update(deps)

    # Filter out internal modules and stdlib
    final_list = sorted([
        d for d in all_external_deps 
        if d not in INTERNAL_PACKAGES and d not in stdlib
    ])

    print("--- Real External Dependencies ---")
    for dep in final_list:
        print(dep)

if __name__ == "__main__":
    main()