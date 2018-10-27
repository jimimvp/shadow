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

def decrypt_command(f, o, passphrase):
    command = f'gpg2 --batch'
    subprocess.call(command.split(' ') + ['--passphrase',passphrase, '-o',o,'--decrypt',f])

def encrypt_command(f, o, passphrase):
    command = f'gpg2 --batch --armor --cipher-algo aes256'
    subprocess.call(command.split(' ') + ['--passphrase',passphrase, '-o',o,'-c',f])


def encrypt_method(directory, output, tar, algo, user):
    passphrase = 'abs'
    confirm = 'abs'
    while passphrase != confirm:

        passphrase = getpass('Passphrase:')
        
        for i in range(3):
            confirm = getpass('Confirm:')
            if confirm == passhprase:
                break
    directory = os.path.abspath(directory)
    if output is None:
        output_tar = directory + '.gzip'
        output_tar_enc = output_tar + '.asc'
        output_enc = directory + '.asc'

    tar_file = tarfile.TarFile(output_tar, 'w')
    file_names = {'nt' : directory+'/names_table'}
    file_paths = []
    os.makedirs(output_enc, exist_ok=True)
    names_table = open(directory+'/names_table', 'wb')
    c = 0
    for root, directories, files in tqdm(os.walk(directory), desc='Scanning files'):
        new_paths = [os.path.join(root, f) for f in files]
        file_paths.extend(new_paths)
        file_names.update({hashlib.sha256(bytes(cu+c)).hexdigest(): f for cu,f in enumerate(new_paths)})
        c+=len(files)

    output_names = {v:k for k,v in file_names.items()}
    pickle.dump(file_names, names_table)
    output_names[directory+'/names_table'] = 'nt'
    print(f'Scanned {len(file_paths)} files')

    #encrypt names table
    file_paths.append(directory+'/names_table')
    file_paths = reversed(file_paths)

    for filepath, output_name in tqdm(output_names.items(), desc='Encrypting files'):
        output_path = f'{output_enc}/{output_name}'
        encrypt_command(filepath, output_path, passphrase)


def decrypt_method(directory, output, tar, algo, user):
    passphrase = 'abs'

    #passphrase = getpass('Passphrase:')
        
    directory = os.path.abspath(directory)
    
    if output is None:
        output_dec = directory.replace('.asc', '')
    else:
        output_dec = output
    file_names = {'nt' : directory+'/names_table'}
    os.makedirs(output_dec, exist_ok=True)
    decrypt_command(directory+'/nt',output_dec+'/names_table', passphrase)

    names_table = pickle.load(open(output_dec+'/names_table', 'rb'))
    output_names = {v:k for k,v in file_names.items()}


    for enc_name, real_name in tqdm(names_table.items(), desc='Decrypting'):
        real_name = real_name.split('/')[-1]
        output_file = f'{output_dec}/{real_name}'
        input_file = f'{directory}/{enc_name}'
        decrypt_command(input_file, output_file, passphrase)


@click.command()
@click.option('--encrypt/--decrypt', '-e', is_flag=True, default=False, help='Encrypt file or folder')
@click.option('--directory', '-d', default=None, help='Target folder')
@click.option('--tar', '-t', default=False, is_flag=True, help='Compress then encrypt')
@click.option('--output', '-o', default='test', help='Output file')
@click.option('--algo', '-a', default='aes256', help='Encryption algorithm')
@click.option('--user', '-u', default=None, help='Asymmetric public key encryption')
def main(encrypt, directory, output, tar, algo, user):
        
    if encrypt:
        encrypt_method(directory, output, tar, algo, user)
    else:
        decrypt_method(directory, output, tar, algo, user)


if __name__ == '__main__':
    main()