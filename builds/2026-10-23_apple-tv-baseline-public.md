# Apple TV Security Baseline v1

**Captured:** October 23, 2026
**Target:** Apple TV HD; device nickname and unique identifiers withheld
**Status:** Baseline complete

## Public-copy scope

This is a public-safe summary of a read-only baseline. The original transcript is
not included. Device and network identifiers, account and key identifiers,
fingerprints, exact service ports, and detailed access-policy output have been
omitted. No passwords, tokens, private keys, or other authentication secrets
are included.

## Summary

The device was operational with a rootful jailbreak environment and package
manager present. Remote administration was working, and a privileged,
read-only follow-up confirmed that the SSH access policy was broader than
necessary for routine administration. In particular, administrative login and
interactive/password-based authentication were permitted. The precise accounts,
listeners, and effective configuration are intentionally not reproduced here.

The capture did not change device configuration. It did not establish whether
the administrative service was reachable beyond the trusted home network, and
it is not evidence of compromise.

## Baseline observations

- The target was an Apple TV HD running tvOS with an active rootful jailbreak.
- The bootstrap and package-management environment were present and operational.
- Remote SSH access using a key was verified; privileged read-only inspection
  was performed separately by the operator.
- A normal user had broad privilege elevation available after authentication.
- Storage was reported healthy, with approximately 4.3 GiB used in the variable
  data area and approximately 17 GiB available.
- No reboot, package change, service restart, or security-policy change was
  performed during the baseline.

## Security assessment

The observed remote-administration policy allowed more access methods and
privilege than routine administration required. This creates a larger attack
surface if the service is exposed through port forwarding, an untrusted VLAN,
or a tunnel. Network exposure was not verified as part of this read-only
baseline.

Recommended follow-up, as a separately planned and tested change:

1. Keep a working administrative session open and verify a recovery path.
2. Disable direct privileged-account login.
3. Disable password-based interactive SSH authentication after confirming that
   key-based administration works independently.
4. Review whether all SSH listeners are necessary and restrict reachability to
   trusted management networks.
5. Recheck the effective policy after the change without publishing its
   identifiers or full configuration.

No hardening change was made during this baseline. The public copy deliberately
does not contain the exact policy output, listener details, or key fingerprints.

## Privacy and evidence handling

The source capture contained a private management address, a hardware MAC
address, device and account identifiers, and SSH public-key and host-key
fingerprints. These are omitted from this public report. Fingerprints are not
private keys, but they can identify a device or key and are unnecessary here.
Keep the original transcript and any detailed evidence in private storage; do
not add them to the public repository.

## Limitations

This is a point-in-time baseline. It does not establish current reachability,
whether the policy has since changed, or whether the reported device state
persists after reboot. Exact version/build details, raw command output, and
network identifiers are intentionally withheld from this public summary.
