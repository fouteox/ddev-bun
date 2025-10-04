#!/usr/bin/env python3
#ddev-generated

import os
import json
import sys

# Platform variants for common packages with native binaries
PLATFORM_VARIANTS = {
    'lightningcss': [
        'lightningcss-linux-arm64-gnu',
        'lightningcss-linux-x64-gnu',
        'lightningcss-darwin-arm64',
        'lightningcss-darwin-x64'
    ],
    '@tailwindcss/oxide': [
        '@tailwindcss/oxide-linux-arm64-gnu',
        '@tailwindcss/oxide-linux-x64-gnu',
        '@tailwindcss/oxide-darwin-arm64',
        '@tailwindcss/oxide-darwin-x64'
    ],
    '@rollup/rollup': [
        '@rollup/rollup-linux-arm64-gnu',
        '@rollup/rollup-linux-x64-gnu',
        '@rollup/rollup-darwin-arm64',
        '@rollup/rollup-darwin-x64'
    ],
    'esbuild': [
        'esbuild-linux-arm64',
        'esbuild-linux-x64',
        'esbuild-darwin-arm64',
        'esbuild-darwin-x64'
    ]
}

def find_package_json():
    package_json = os.path.join(os.getcwd(), "package.json")
    if os.path.isfile(package_json):
        return package_json
    return None

def detect_package_base(package_name):
    """Detect which base package this variant belongs to"""
    for base, variants in PLATFORM_VARIANTS.items():
        if any(package_name.startswith(variant.split('-')[0]) for variant in variants):
            return base
    return None

def get_version_from_existing(optional_deps, variants):
    """Get version from any existing variant"""
    for variant in variants:
        if variant in optional_deps:
            return optional_deps[variant]
    return None

def add_platform_variants(data):
    """Add missing platform variants to optionalDependencies"""
    if 'optionalDependencies' not in data:
        return data

    optional_deps = data['optionalDependencies']
    new_deps = {}

    # Check each base package
    for base, variants in PLATFORM_VARIANTS.items():
        # Find if any variant exists
        version = get_version_from_existing(optional_deps, variants)

        if version:
            # Add all variants with the same version
            for variant in variants:
                if variant not in optional_deps:
                    new_deps[variant] = version

    # Merge new dependencies
    data['optionalDependencies'].update(new_deps)

    return data

def main():
    if 'DDEV_APPROOT' in os.environ:
        os.chdir(os.environ['DDEV_APPROOT'])
    elif os.path.exists('/app'):
        os.chdir('/app')

    package_json = find_package_json()
    if not package_json:
        print("No package.json found", file=sys.stderr)
        sys.exit(1)

    backup_file = None
    try:
        # Read package.json
        with open(package_json, 'r') as f:
            data = json.load(f)

        # Create backup
        backup_file = package_json + ".bak"
        with open(backup_file, 'w') as f:
            json.dump(data, f, indent=4)

        # Add platform variants
        data = add_platform_variants(data)

        # Save package.json
        with open(package_json, 'w') as f:
            json.dump(data, f, indent=4)
            f.write('\n')  # Add trailing newline

        # Remove backup on success
        os.remove(backup_file)

        print("Successfully updated package.json with platform variants")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if backup_file and os.path.exists(backup_file):
            os.replace(backup_file, package_json)
        sys.exit(1)

if __name__ == "__main__":
    main()
