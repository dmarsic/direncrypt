# direncrypt

Sync directories with unencrypted and encrypted files using GPG encryption functions.

## Quick Intro

**encrypt.py** allows you to easily keep your files in sync between unencrypted (source) directory and encrypted (destination) directory. One use case might be to encrypt your files (code, documents) when putting them to Dropbox by saving them to local directory and having a scheduled job running **encrypt.py** to encrypt them to Dropbox directory.

### First Setup

Check *Dependencies* below if the program does not run due to missing dependencies.

**direncrypt** requires SQLite database `inventory.sqlite`. Ensure that *sqlite3* is available and run:

```
sqlite3 inventory.sqlite < schema.sql
```

It is assumed that GPG has been configured on the host. If not, this is the place to start: https://gnupg.org/

Additionally, GPG 2.1 requires an additional parameter in `gpg-agent.conf`. If the file does not exist, create it.

```
allow-loopback-pinentry
```

A recommended next step is to set GPG parameters by running:

```
python encrypt.py --configure
```

Some defaults have been pre-set. To change them, specify `key value`, as shown in the example below:

```
PARAMETER       VALUE
----------------------------------------
plaindir        ~/DropboxLocal
securedir       ~/Dropbox/Enc
public_id       None
gpg_keyring     pubring.kbx
gpg_homedir     ~/.gnupg
gpg_binary      gpg2

parameters> plaindir ~/DropboxUnencrypted
Setting plaindir to: ~/DropboxUnencrypted
```

### Usage Examples

1) Program is already configured, encrypt all files that have not been encrypted since the last run:

```
encrypt.py -e
```

2) Program is already configured, decrypt all files found in register from encrypted (destination) to source directory:

```
encrypt.py -d
```

3) Program is not yet configured, or we want to override some parameters, and encrypt unencrypted files:

```
encrypt.py --encrypt \
           --plaindir ~/DropboxLocal \
           --securedir ~/Dropbox/Enc \
           --public-id BADCOFFE \
           --gpg-homedir ~/.gnupg \
           --gpg-keyring pubring.kbx \
           --gpg-binary gpg2
```

4) Decrypt all files to another location:

```
encrypt.py -d --plaindir ~/NewLocation
```

### Command-line options

```
encrypt.py OPERATION PARAMETERS -v|--verbose

OPERATION
    -e|--encrypt     Encrypts new files from unencrypted directory to encrypted directory
    -d|--decrypt     Decrypts files encrypted with the specified public ID from encrypted
                     to unencrypted directory
       --configure   Runs interactive mode to list and set GPG parameters

PARAMETERS
    -p|--plaindir
    -s|--securedir
    -i|--public-id
    -P|--passphrase
    -H|--gpg-homedir
    -k|--gpg-keyring
    -b|--gpg-binary
```
## Check Consistency

`list.py` provides a listing of files based on the register, and also checks the existence of files on the filesystem. The listing is provided in the format similar to this:

```
Plaindir: ~/DropboxLocal
Securedir: ~/Dropbox/Enc

STATUS PLAINFILE                           ENCFILE
ok  ue subdir/newfile.txt                  398a8fc1-1c33-4e2b-80a2-ae8645007cba
ok  ue test1.txt                           97f204c5-bdcb-4e61-9f7b-ec4bc9fd6824
NOK u  test2.txt                           75d49d5c-bc4c-46ad-b286-c336cc170aff
ok  ue subdir/another.txt                  6471eef4-8a8a-4fb5-858b-200cdcd7b231
NOK  e test3.txt                           cc1f2d27-c006-4d01-8c5d-b356ce482a30

Total files in the register: 5
Check: 3 ok, 2 not ok
```

State can be inconsistent if the files have been deleted but the register has not been updated. This needs to be done manually at the moment.

## direncryption Library

**direncryption.py** provides functions used by **encrypt.py**. Two main methods are **encrypt_all()** and **decrypt_all()**.

**encrypt_all()** gets a list of all files under the unencrypted directory and compares their modified time with saved timestamps in database. New files and files modified after the last run will be encrypted.

**decrypt_all()** reads the register to get the list of files encrypted using the same GPG public ID as the one running now. Then it decrypts all such files using the passphrase provided.

## inventory.sqlite Database

This database contains mapping between unencrypted filenames and encrypted filenames, as well as GPG public ID used to encrypt. If lost, there is no way to know where encrypted file originates from. It is recommended to keep a backup of the database in a safe and secure location.

## Dependencies

* GnuPG: https://gnupg.org/
* Python modules: `python-gnupg` (https://github.com/vsajip/python-gnupg), `sqlite3`

`lib/direncrypt/gpgops.py` imports `gnupg`. Ensure that `gnupg.py` is found. Some options include adding path to it to `PYTHONPATH` or linking to `gnupg.py` from `lib/direncrypt` directory (I would not recommend the latter).

## License

See `LICENSE` file.

## Author

Domagoj Marsic

<dmars@protonmail.com>
