
import hashlib
import secrets

from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes


class CustomScryptPasswordHasher(BasePasswordHasher):
    algorithm = "custom_scrypt"

    # scrypt cost parameters
    work_factor = 2**14
    block_size = 8
    parallelism = 1
    key_length = 64

    def salt(self):
        return secrets.token_hex(16)

    def encode(self, password, salt):
        if password is None:
            raise TypeError("Password cannot be None")

        derived_key = hashlib.scrypt(
            force_bytes(password),
            salt=force_bytes(salt),
            n=self.work_factor,
            r=self.block_size,
            p=self.parallelism,
            dklen=self.key_length,
        )

        return (
            f"{self.algorithm}${self.work_factor}$"
            f"{self.block_size}${self.parallelism}$"
            f"{salt}${derived_key.hex()}"
        )

    def verify(self, password, encoded):
        try:
            algorithm, n, r, p, salt, stored_hash = encoded.split("$")
            if algorithm != self.algorithm:
                return False

            derived_key = hashlib.scrypt(
                force_bytes(password),
                salt=force_bytes(salt),
                n=int(n),
                r=int(r),
                p=int(p),
                dklen=len(bytes.fromhex(stored_hash)),
            )

            return constant_time_compare(
                derived_key.hex(),
                stored_hash,
            )
        except (ValueError, TypeError, OverflowError):
            return False

    def safe_summary(self, encoded):
        algorithm, n, r, p, salt, stored_hash = encoded.split("$")

        return {
            "algorithm": algorithm,
            "work factor": n,
            "block size": r,
            "parallelism": p,
            "salt": mask_hash(salt),
            "hash": mask_hash(stored_hash),
        }

    def must_update(self, encoded):
        try:
            _, n, r, p, _, _ = encoded.split("$")
            return (
                int(n) != self.work_factor
                or int(r) != self.block_size
                or int(p) != self.parallelism
            )
        except (ValueError, TypeError):
            return True
