# STM32H7S3 Option Bytes

## Scope

The MCP exposes option-byte **inspection** as a first-class operation and keeps
option-byte modification behind explicit safety policy.

For STM32H7S3, option bytes are controlled through the FLASH peripheral. RM0477
documents `FLASH_OPTKEYR`, `FLASH_OPTCR`, `FLASH_OPTISR`, `FLASH_OPTICR`,
`FLASH_OBKCR`, the option-byte key data registers, and the current/programming
option-byte status registers.

### Read

The safe read path should report both:

- current (`*_CUR` / status) values
- programming (`*_PRG`) values where the device exposes them

The MCP should never interpret a raw value as a human-readable setting unless
the field definition is verified against the exact STM32H7S3 reference manual.

### Write

Option-byte writes are **not equivalent to ordinary memory writes**.

The STM32H7S3 requires the device-specific option-byte unlock/program/launch
sequence. Changing option bytes can alter boot behavior, protection, debug
access, voltage configuration, and other persistent device state.

Therefore:

- `allow_write` defaults to false.
- A write must use the exact STM32H7S3 register sequence.
- The implementation must read back the resulting current values after launch.
- The operation must report that the device may reset/reload option bytes.
- RDP/security/irreversible settings require an additional dedicated safety
  policy rather than a generic "write register" path.

### Mass erase

Mass erase is destructive and is separate from ordinary flash erase.

The MCP requires the explicit token:

`MASS_ERASE_INTERNAL_FLASH`

The implementation should use a device-aware programming backend rather than
blindly setting a guessed FLASH register bit.

## SEGGER integration

SEGGER's current documentation shows that its STM32 tooling/Device Provisioner
can perform device-specific option-byte operations using J-Link scripts. This
is preferable to guessing a generic J-Link Commander command for a new STM32
family.

For this project, a future implementation should provide an
`OptionBytesBackend` with:

```text
read_current()
read_programming()
write()
launch()
mass_erase()
verify()
```

and select the implementation based on the exact STM32H7S3 device profile.

## Important

Do not add support for RDP/HDPL/secure-area/OTP/key programming simply by
exposing raw 32-bit register writes. Those operations need explicit device
documentation, policy, and hardware validation.
