#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import errno
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

try:
    from OpenSSL import crypto
except ImportError:
    pyopenssl_found = False
else:
    pyopenssl_found = True


class CertificateSigningRequestError(Exception):
    pass


class CertificateSigningRequest(object):

    def __init__(self, module):
        self.state = module.params['state']
        self.digest = module.params['digest']
        self.force = module.params['force']
        self.subjectAltName = module.params['subjectAltName']
        self.path = module.params['path']
        self.privatekey_path = module.params['privatekey_path']
        self.version = module.params['version']
        self.changed = True
        self.request = None
        self.privatekey = None

        self.subject = {
            'C': module.params['countryName'],
            'ST': module.params['stateOrProvinceName'],
            'L': module.params['localityName'],
            'O': module.params['organizationName'],
            'OU': module.params['organizationalUnitName'],
            'CN': module.params['commonName'],
            'emailAddress': module.params['emailAddress'],
        }

        if self.subjectAltName is None:
            self.subjectAltName = 'DNS:%s' % self.subject['CN']

        self.subject = dict((k, v) for k, v in self.subject.items() if v)

    def generate(self, module):
        '''Generate the certificate signing request.'''

        if not os.path.exists(self.path) or self.force:
            req = crypto.X509Req()
            req.set_version(self.version)
            subject = req.get_subject()
            for (key, value) in self.subject.items():
                if value is not None:
                    setattr(subject, key, value)

            if self.subjectAltName is not None:
                req.add_extensions([crypto.X509Extension(
                    b"subjectAltName", False,
                    self.subjectAltName.encode('ascii'))])

            privatekey_content = open(self.privatekey_path).read()
            self.privatekey = crypto.load_privatekey(
                crypto.FILETYPE_PEM, privatekey_content)

            req.set_pubkey(self.privatekey)
            req.sign(self.privatekey, self.digest)
            self.request = req

            try:
                csr_file = open(self.path, 'wb')
                csr_file.write(crypto.dump_certificate_request(
                    crypto.FILETYPE_PEM, self.request))
                csr_file.close()
            except (IOError, OSError) as exc:
                raise CertificateSigningRequestError(exc)
        else:
            self.changed = False

        file_args = module.load_file_common_arguments(module.params)
        if module.set_fs_attributes_if_different(file_args, False):
            self.changed = True

    def remove(self):
        '''Remove the Certificate Signing Request.'''

        try:
            os.remove(self.path)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise CertificateSigningRequestError(exc)
            else:
                self.changed = False

    def dump(self):
        '''Serialize the object into a dictionary.'''

        result = {
            'csr': self.path,
            'subject': self.subject,
            'subjectAltName': self.subjectAltName,
            'changed': self.changed
        }

        return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=[
                       'present', 'absent'], type='str'),
            digest=dict(default='sha256', type='str'),
            privatekey_path=dict(require=True, type='path'),
            version=dict(default='3', type='int'),
            force=dict(default=False, type='bool'),
            subjectAltName=dict(aliases=['subjectAltName'], type='str'),
            path=dict(required=True, type='path'),
            countryName=dict(aliases=['C'], type='str'),
            stateOrProvinceName=dict(aliases=['ST'], type='str'),
            localityName=dict(aliases=['L'], type='str'),
            organizationName=dict(aliases=['O'], type='str'),
            organizationalUnitName=dict(aliases=['OU'], type='str'),
            commonName=dict(aliases=['CN'], type='str'),
            emailAddress=dict(aliases=['E'], type='str'),
        ),
        add_file_common_args=True,
        supports_check_mode=True,
        required_one_of=[['commonName', 'subjectAltName']],
    )

    if not pyopenssl_found:
        module.fail_json(msg='the python pyOpenSSL module is required')

    path = module.params['path']
    base_dir = os.path.dirname(module.params['path'])

    if not os.path.isdir(base_dir):
        module.fail_json(
            name=path, msg='The directory %s does not exist' % path)

    csr = CertificateSigningRequest(module)

    if module.params['state'] == 'present':

        if module.check_mode:
            result = csr.dump()
            result['changed'] = module.params['force'] or not os.path.exists(
                path)
            module.exit_json(**result)

        try:
            csr.generate(module)
        except CertificateSigningRequestError as exc:
            module.fail_json(msg=to_native(exc))

    else:

        if module.check_mode:
            result = csr.dump()
            result['changed'] = os.path.exists(path)
            module.exit_json(**result)

        try:
            csr.remove()
        except CertificateSigningRequestError as exc:
            module.fail_json(msg=to_native(exc))

    result = csr.dump()

    module.exit_json(**result)


if __name__ == "__main__":
    main()
