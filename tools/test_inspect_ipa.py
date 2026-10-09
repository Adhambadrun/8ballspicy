import hashlib
import struct
import unittest
from inspect_ipa import macho


class MachOInspectionTests(unittest.TestCase):
    def test_arm64_object_is_not_application(self):
        b = struct.pack('<8I', 0xfeedfacf, 0x100000c, 0, 1, 0, 0, 0, 0)
        result = macho(b)
        self.assertEqual(result['architecture'], 'arm64')
        self.assertEqual(result['file_type'], 1)
        self.assertFalse(result['code_signature']['present'])

    def test_signature_hash_match_then_detect_mutation(self):
        # Synthetic fixture, not an Apple-issued signature and never exported.
        page = 4096
        prefix = bytearray(page)
        struct.pack_into('<8I', prefix, 0, 0xfeedfacf, 0x100000c, 0, 2, 1, 16, 0, 0)
        ident = b'test.fixture\0'
        ho = 44+len(ident)
        cdsize = ho+32
        blobsize = 20+cdsize
        struct.pack_into('<4I', prefix, 32, 0x1d, 16, page, blobsize)
        cd = bytearray(cdsize)
        struct.pack_into('>9I', cd, 0, 0xfade0c02, cdsize, 0x20000, 0, ho, 44, 0, 1, page)
        struct.pack_into('>4B', cd, 36, 32, 2, 0, 12)
        cd[44:ho] = ident
        cd[ho:] = hashlib.sha256(prefix).digest()
        sb = struct.pack('>5I', 0xfade0cc0, blobsize, 1, 0, 20)+cd
        result = macho(bytes(prefix)+sb)
        d = result['code_signature']['code_directories'][0]
        self.assertEqual(d['page_hash_mismatches'], 0)
        prefix[100] ^= 1
        d = macho(bytes(prefix)+sb)['code_signature']['code_directories'][0]
        self.assertEqual(d['page_hash_mismatches'], 1)
        self.assertEqual(d['mismatches_wholly_before_signature'], 1)

    def test_invalid_command_is_rejected(self):
        b = struct.pack('<8I', 0xfeedfacf, 0x100000c, 0, 2, 1, 8, 0, 0)+struct.pack('<2I',1,4)
        with self.assertRaises(ValueError):
            macho(b)

    def test_non_macho_is_not_guessed(self):
        self.assertIn('unsupported', macho(b'PK00')['format'])


if __name__ == '__main__':
    unittest.main()
