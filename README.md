# Shadow

This package is a simple interface to gpg for symmetric encyption functionality. Contributions are welcome, it is still in early development.

## Installation

To install the package, clone the repo and then:

`pip install -U . `

Alternatively from the repo directly:

`pip install -U git+[repo_url]`

For development:

`pip install --editable -U .`


## Usage

Example usage:

`shadow --encrypt path_to_dir -o output --algo aes256`
`shadow --decrypt path_to_dir -o output --algo aes256`
`shadow --help`

To look at the encrypted files:

`shadow --list path_to_encrypted_dir`

To act only on files based on regex:

`shadow --decrypt path_to_dir -o output --algo aes256 --regex boom`

**DISCLAIMER: be careful with your data, this package is still in development, use at your own risk**