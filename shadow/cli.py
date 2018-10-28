import click
from tqdm import tqdm
import getpass
import os
from subprocess import Popen, PIPE, STDOUT
import subprocess
import tarfile
from tqdm import tqdm
import pickle
import hashlib

#gpg2 --batch --passphrase-fd 0 --armor -r edward --encrypt -c --cipher-algo aes256

def escape_chars(s):
    for c in [',', ' ', '(', ')', '[', ']', '{', '}',]:
        s = s.replace(c, '\\'+c)
    return s

def decrypt_command(f, o, passphrase, algo='aes256'):
    command = f'gpg --batch --quiet'
    subprocess.call(command.split(' ') + ['--passphrase',passphrase, '--output',o,'--decrypt',f])

def encrypt_command(f, o, passphrase, algo='aes256'):
    print(f, o)
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
 


def encrypt_method(directory, output, tar, algo, user, overwrite):
    passphrase = 'abs'
    confirm = 'abs'
    while passphrase != confirm:

        passphrase = getpass('Passphrase:')
        
        for i in range(3):
            confirm = getpass('Confirm:')
            if confirm == passhprase:
                break
    root_dir = os.path.abspath(directory)
    if output is None:
        output_tar = root_dir + '.gzip'
        output_tar_enc = output_tar + '.asc'
        output_enc = root_dir + '.asc'
    else:
        output_enc = output

    file_names = {'nt' : root_dir+'/names_table'}
    file_paths = []


    os.makedirs(output, exist_ok=True)
    names_table_f = open(root_dir+'/names_table', 'wb')
    c = 0
    for root, directories, files in tqdm(os.walk(root_dir), desc='Scanning files'):
        new_paths = [os.path.join(root, f) for f in files]
        file_paths.extend(new_paths)
        file_names.update({hashlib.sha256(bytes(cu+c)).hexdigest(): f for cu,f in enumerate(new_paths)})
        c+=len(files)

    output_names = {v:k for k,v in file_names.items()}
    relative_paths = {k: filter_root(root_dir, v)  for k,v in file_names.items() if not('names_table' in v  and not 'nt' in k)}
    pickle.dump(relative_paths, names_table_f)
    names_table_f.close()

    output_names[root_dir+'/names_table'] = 'nt'
    print(f'Scanned {len(file_paths)} files')


    #encrypt names table
    file_paths.append(root_dir+'/names_table')
    file_paths = reversed(file_paths)

    for filepath, output_name in tqdm(output_names.items(), desc='Encrypting files'):
        output_path = f'{output_enc}/{output_name}'
        if output_name == 'nt':
            print('YSAY', filepath)
        if handle_existing(output_path, overwrite):
            encrypt_command(filepath, output_path, passphrase, algo)


def decrypt_method(directory, output, tar, algo, user, overwrite):
    passphrase = 'abs'

    #passphrase = getpass('Passphrase:')
        
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
        relative_path = relative_path
        output_file = f'{output_dec}/{relative_path}'
        splitted = output_file.split('/')
        if len(splitted) > 1:
            os.makedirs('/'.join(splitted[:-1]), exist_ok=True)
        input_file = f'{root_dir}/{enc_name}'

        if handle_existing(output_file, overwrite):
            decrypt_command(input_file, output_file, passphrase)


@click.command()
@click.option('--encrypt/--decrypt', '-e', is_flag=True, default=True, help='Encrypt file or folder')
@click.option('--directory', '-d', default=None, help='Target folder')
@click.option('--tar', '-t', default=False, is_flag=True, help='Compress then encrypt')
@click.option('--output', '-o', default=None, help='Output file')
@click.option('--algo', '-a', default='aes256', help='Encryption algorithm')
@click.option('--user', '-u', default=None, help='Asymmetric public key encryption')
@click.option('--overwrite', '-ow', default=False, help='Asymmetric public key encryption')
@click.option('--test', '-te', default=False, is_flag=True, help='Run test')
def main(encrypt, directory, output, tar, algo, user, overwrite):
    if encrypt and test:
        output = '/Users/Jimmy/Desktop/safe_test.asc'
        directory = '/Users/Jimmy/Desktop/safe_test'
    elif test:
        output = '/Users/Jimmy/Desktop/safe_test_dec'
        directory = '/Users/Jimmy/Desktop/safe_test.asc'
    
    if encrypt:
        encrypt_method(directory, output, tar, algo, user, overwrite)
    else:
        decrypt_method(directory, output, tar, algo, user, overwrite)


if __name__ == '__main__':
    main()