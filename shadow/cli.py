import click
from tqdm import tqdm
from getpass import getpass
import os
from subprocess import Popen, PIPE, STDOUT
import subprocess
import tarfile
from tqdm import tqdm
import pickle
import hashlib
from pprint import pprint

def escape_chars(s):
    for c in [',', ' ', '(', ')', '[', ']', '{', '}',]:
        s = s.replace(c, '\\'+c)
    return s

def decrypt_command(f, o, passphrase, algo='aes256'):
    command = f'gpg --batch --quiet'
    subprocess.call(command.split(' ') + ['--passphrase',passphrase, '--output',o,'--decrypt',f])

def encrypt_command(f, o, passphrase, algo='aes256'):
    command = f'gpg --batch --quiet --cipher-algo {algo}'
    subprocess.call(command.split(' ') + ['--passphrase',passphrase, '--output',o,'-c',f])

def filter_root(root, path):
    return path.replace(root+'/', '')

def handle_existing(f, overwrite=True):
    if os.path.exists(f) and not overwrite:
        print('Skipping existing file: ', f)
        return False
    elif os.path.exists(f):
        print('Removing: ', f)
        os.remove(f)
    return True
 
def regex_satisfied(f, regex):
    if regex:
        return regex in f 
    else:
        return True

def encrypt_method(directory, output, tar, algo, user, overwrite, regex):
    passphrase = 'abs'
    confirm = None
    while passphrase != confirm:

        passphrase = getpass('Passphrase:')
        
        for i in range(3):
            confirm = getpass('Confirm:')
            if confirm == passphrase:
                break
    root_dir = os.path.abspath(directory)

    if output is None:
        output_enc = root_dir + '.asc'
    else:
        output_enc = output

    file_names = {'nt' : root_dir+'/names_table'}
    file_paths = []

    os.makedirs(output_enc, exist_ok=True)
    names_table_path = root_dir+'/names_table'
    names_table_f = open(names_table_path, 'wb')
    c = 0
    for root, directories, files in tqdm(os.walk(root_dir), desc='Scanning files'):
        new_paths = [os.path.join(root, f) for f in files if regex_satisfied(f, regex)]
        file_paths.extend([p for p in new_paths])
        file_names.update({hashlib.sha256(bytes(cu+c)).hexdigest(): f for cu,f in enumerate(new_paths)})
        c+=len(files)

    output_names = {v:k for k,v in file_names.items()}
    relative_paths = {k: filter_root(root_dir, v)  for k,v in file_names.items() if not('names_table' in v  and not 'nt' in k)}
    
    pickle.dump(relative_paths, names_table_f)
    names_table_f.close()
    if handle_existing(f'{output_enc}/nt', overwrite):
        encrypt_command(names_table_path, f'{output_enc}/nt', passphrase, algo)

    os.remove(names_table_path)

    print(f'Scanned {len(file_paths)} files')

    #encrypt names table

    for filepath, output_name in tqdm(output_names.items(), desc='Encrypting files'):
        output_path = f'{output_enc}/{output_name}'
        if handle_existing(output_path, overwrite):
            encrypt_command(filepath, output_path, passphrase, algo)





def list_encrypted(directory, algo):

    passphrase = getpass('Passphrase:')
        
    root_dir = os.path.abspath(directory)

    decrypt_command(root_dir+'/nt','names_table', passphrase, algo)
    
    names_table = pickle.load(open('names_table', 'rb'))
    os.remove('names_table')
    print('\n'.join(names_table.values()))



def decrypt_method(directory, output, tar, algo, user, overwrite, regex):

    passphrase = getpass('Passphrase:')
        
    root_dir = os.path.abspath(directory)
    
    if output is None:
        output_dec = root_dir.replace('.asc', '')
    else:
        output_dec = output
    file_names = {'nt' : root_dir+'/names_table'}

    os.makedirs(output_dec, exist_ok=True)
    if handle_existing(output_dec+'/names_table', overwrite):
        decrypt_command(root_dir+'/nt',output_dec+'/names_table', passphrase, algo)
    names_table = pickle.load(open(output_dec+'/names_table', 'rb'))
    output_names = {v:k for k,v in file_names.items()}

    for enc_name, relative_path in tqdm(names_table.items(), desc='Decrypting'):
        if not regex_satisfied(relative_path, regex):
            continue

        output_file = f'{output_dec}/{relative_path}'
        splitted = output_file.split('/')
        if len(splitted) > 1:
            os.makedirs('/'.join(splitted[:-1]), exist_ok=True)
        input_file = f'{root_dir}/{enc_name}'

        if handle_existing(output_file, overwrite):
            decrypt_command(input_file, output_file, passphrase)


@click.command()
@click.option('--encrypt', '-e', default=None, help='Encrypt target')
@click.option('--decrypt', '-d', default=None, help='Decrypt target')
@click.option('--tar', '-t', default=False, is_flag=True, help='Compress then encrypt')
@click.option('--output', '-o', default=None, help='Output file')
@click.option('--algo', '-a', default='aes256', help='Encryption algorithm')
@click.option('--user', '-u', default=None, help='Asymmetric public key encryption')
@click.option('--overwrite', '-ow', default=False, is_flag=True, help='Asymmetric public key encryption')
@click.option('--test', '-te', default=False, is_flag=True, help='Run test')
@click.option('--regex', '-re', default=None, help='Only files that satisfy this regular expression')
@click.option('--lis', '-l', default=None, help='List encrypted files in target')
def main(encrypt, decrypt, output, lis,
    tar, algo, user, overwrite, test, regex):
    
    if lis:
        list_encrypted(lis, algo)
    elif encrypt:
        encrypt_method(encrypt, output, tar, algo, user, overwrite, regex)
    else:
        decrypt_method(decrypt, output, tar, algo, user, overwrite, regex)


if __name__ == '__main__':
    main()