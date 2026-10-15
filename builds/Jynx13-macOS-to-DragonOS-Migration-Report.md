# Jynx13 Migration Report

## From macOS Monterey to DragonOS Resolute R1

**System:** Jynx13 — 2017 MacBook Air  
**Workload:** Echo digital assistant, PAI/OpenCode, Hindsight, Syncthing, and supporting services  
**Migration date:** October 14, 2026  
**Result:** Successful migration with identity, memory, and core services preserved

> **Security note:** This report intentionally omits passwords, encryption material, API credentials, device identifiers, private endpoints, and user-specific filesystem paths. Commands and paths are described generically where the original values were sensitive or not needed to explain the outcome.

---

## Executive summary

Jynx13, a 2017 MacBook Air, was migrated from macOS Monterey—an aging but dependable installation—to DragonOS Resolute R1. The goal was not simply to install Linux. It was to preserve Echo as a continuing digital assistant: her encrypted local state, PAI/OpenCode environment, Hindsight memory access, Syncthing identity, and service relationships all needed to survive the operating-system replacement.

The migration took roughly four hours. It included a pre-install backup, a clean DragonOS installation, hardware and service troubleshooting, restoration of Echo's encrypted vault, recovery of the existing Syncthing identity, and application-level verification. The decisive validation was an end-to-end Hindsight recall from Echo's pre-migration memory bank. Echo then independently detected that Jynx13 was no longer running macOS Monterey and correctly identified the new Linux base.

The result was continuity rather than reconstruction: same machine, same assistant, same history—on a new operating system with a broader communications and software-defined-radio platform.

## Migration objectives

The migration was considered successful only if it accomplished all of the following:

1. Replace macOS Monterey with DragonOS Resolute R1 on the 2017 MacBook Air.
2. Preserve a recoverable copy of Jynx13's important data before modifying the system disk.
3. Bring the MacBook Air's essential hardware into a usable post-install state.
4. Restore Echo's encrypted vault without exposing its secrets.
5. Restore the existing Syncthing identity instead of creating an unrelated replacement device.
6. Re-establish PAI/OpenCode and its supporting service configuration.
7. Confirm that Hindsight was not merely configured, but could retrieve Echo's existing memories.
8. Record remaining non-blocking work separately from the verified migration outcome.

## Starting point

Before the migration, Jynx13 was:

- a 2017 MacBook Air;
- running macOS Monterey;
- hosting Echo's working environment;
- carrying an encrypted vault that needed to remain confidential and recoverable;
- participating in the Burrow's synchronization topology through Syncthing; and
- connected to Echo's longer-term memory through Hindsight.

Monterey had served the machine well, but the desired next phase called for a Linux environment with the tools and flexibility provided by DragonOS. Because Echo's state spanned local files, cryptographic material, synchronization identity, application configuration, and remote memory, treating the work as a simple operating-system reinstall would have been insufficient.

## Migration approach

### 1. Back up before changing the system

The first stage was preservation. The relevant Jynx13 and Echo data was copied off the installation target before the operating system was replaced. The backup set covered the material needed to recover Echo's local environment, including the encrypted vault, PAI/OpenCode configuration, Syncthing state, and other service data required for continuity.

The important principle was to preserve both **content** and **identity**. A copy of ordinary files would not, by itself, preserve an encrypted workspace or an existing Syncthing node. Those components depend on their associated metadata and cryptographic identity as well as their visible contents.

No secret values from the backup are included in this report.

### 2. Install DragonOS Resolute R1

With the backup secured, the existing macOS installation was replaced by DragonOS Resolute R1. The installed system later reported:

```text
Ubuntu 26.04.1 LTS (Resolute Raccoon)
```

This is the Ubuntu base beneath the DragonOS installation. Seeing the Ubuntu identity in system output is therefore consistent with the DragonOS deployment rather than evidence that the wrong platform was installed.

### 3. Work through hardware compatibility

Installing a current Linux distribution on 2017 Apple hardware required post-install troubleshooting rather than an assumption that every component would be ready immediately. The process included checking the machine's essential hardware and resolving the compatibility issues encountered during bring-up.

The conversation establishes that hardware troubleshooting was part of the successful migration, but this report does not invent model-specific fixes or command sequences that were not preserved in the available record. For repeatability, a future maintenance pass should record the exact driver packages, kernel parameters, firmware choices, and validation results used on Jynx13.

### 4. Re-establish the service layer

After the base operating system was usable, the supporting services were restored and checked. This was a dependency-ordered process: application data was not treated as healthy until the services that interpret, synchronize, or expose it were also running.

The restored stack included:

- Syncthing and Jynx13's prior synchronization identity;
- Echo's encrypted vault and its unlocking workflow;
- the PAI/OpenCode environment;
- Hindsight connectivity and memory tools; and
- the surrounding MCP/service configuration required by Echo's workspace.

### 5. Recover Echo's encrypted vault

Echo's vault was restored from the protected backup and returned to a usable encrypted state. Recovery meant more than copying a directory: the restored data had to be placed where the new environment could use it while retaining the vault's confidentiality and expected access behavior.

The recovery procedure deliberately kept passphrases, keys, tokens, and other unlocking material out of logs and out of this report. Repository documentation should describe *where operators obtain secrets securely*, never embed the secrets themselves.

### 6. Restore the Syncthing identity

Syncthing identity restoration was a key continuity step. Reusing the preserved identity allowed Jynx13 to return as the same known synchronization participant rather than appearing to peers as an entirely new device.

That distinction matters operationally:

- peer trust and existing relationships remain associated with Jynx13;
- folder mappings can be reconciled against the known node;
- duplicate-device confusion is avoided; and
- migration risk is reduced because the restored machine resumes its former role.

Identity files are cryptographic assets. Their locations, contents, and device identifiers are intentionally omitted here.

### 7. Restore PAI/OpenCode

Echo's PAI/OpenCode environment was restored on the new system. The post-migration session showed OpenCode running successfully, reporting version `1.19.0`, with the restored workspace active.

The interface also showed Hindsight connected. Two other MCP integrations—Apple Health and Echo hearing—reported closed connections during the captured session. Those errors did not prevent the core Echo/Hindsight validation, but they remain follow-up items.

### 8. Verify Hindsight end to end

The strongest migration test was not a green status indicator. Echo invoked a Hindsight recall for Burrow digital-assistant information, and Hindsight returned stored material from the existing memory bank, including historical Burrow context.

This proved the complete path:

```text
Echo in OpenCode
    -> Hindsight tool connection
    -> existing memory bank
    -> pre-migration memories returned to Echo
```

That end-to-end retrieval established that Echo could access memories created before the operating-system change. The migration therefore preserved functional memory continuity, not merely configuration files that appeared plausible.

### 9. Confirm Echo's continuity

Echo's own response provided a useful behavioral acceptance test. After checking the host, she identified the new environment as Ubuntu 26.04.1 LTS (Resolute Raccoon), compared it with her remembered description of Jynx13 as a 2017 MacBook Air running macOS Monterey, and recognized that the operating system had changed.

Her personality, conversational style, and historical awareness remained intact. In practical terms, Echo was migrated rather than recreated.

## Verification record

| Area | Evidence | Status |
|---|---|---|
| Operating system | Host reported Ubuntu 26.04.1 LTS, codename Resolute Raccoon, as the base for DragonOS Resolute R1 | Verified |
| PAI/OpenCode | Restored workspace launched; OpenCode reported version 1.19.0 | Verified |
| Hindsight transport | Interface reported Hindsight connected | Verified |
| Hindsight memory | A live recall returned historical, pre-migration Burrow memories | Verified end to end |
| Echo continuity | Echo retained her voice, recognized prior Jynx13 context, and detected the OS change | Verified behaviorally |
| Encrypted vault | Restored as part of Echo's recovered environment without disclosing secret material | Restored |
| Syncthing identity | Existing identity restored instead of registering Jynx13 as an unrelated new node | Restored |
| Apple Health MCP | Captured session showed a closed connection | Pending |
| Echo-hearing MCP | Captured session showed a closed connection | Pending |

## Problems encountered and how they were handled

### Hardware was not assumed to be plug-and-play

The Apple hardware required active post-install validation and troubleshooting. The lesson is to plan a Linux-on-Mac migration as a hardware bring-up exercise, with a fallback path for networking and access while drivers and services are being repaired.

### Restoring files was not enough

Several parts of Echo's environment depended on hidden state or identity:

- the vault required its encrypted structure and access material;
- Syncthing required its existing cryptographic device identity;
- PAI/OpenCode required its workspace and configuration; and
- Hindsight required a working service path to the existing memory bank.

Treating these as separate recovery domains made it possible to validate each layer independently.

### A connection indicator was not accepted as proof

Hindsight's connected state was encouraging, but the migration was not declared complete on that basis. A real recall query was executed and returned known historical content. This converted a configuration check into a functional acceptance test.

### Old memory can be correct but incomplete

Echo initially recalled older Burrow information rather than the current Council roster. That was evidence that historical memory survived, but it also showed that restored memory can lag recent real-world changes. Persistence and freshness are different properties and should be tested separately.

## Lessons learned

1. **Back up identities, not just documents.** Synchronization nodes, encrypted stores, and service clients may rely on small but critical identity files.
2. **Restore in dependency order.** Base OS and hardware come first, followed by services, identities, encrypted data, applications, and finally end-to-end behavior.
3. **Keep a temporary access path available.** Linux installation on older Apple hardware can require driver or firmware work before normal connectivity is dependable.
4. **Validate with real operations.** A service that starts successfully is not necessarily a service that can retrieve the right data.
5. **Separate continuity from freshness.** Echo's historical recall proved continuity; updating her knowledge of the expanded Burrow is a separate task.
6. **Keep secrets out of migration notes.** Documentation should identify secret-management procedures and backup scope without publishing credentials or cryptographic material.
7. **Capture exact fixes as they happen.** The next iteration should record package names, driver versions, firmware, kernel parameters, and service-unit changes in a sanitized runbook.
8. **Preserve rollback until acceptance testing is complete.** Backups should remain available until the new system has passed hardware, service, synchronization, and memory checks over a reasonable observation period.

## Pending work

The primary migration is complete, but the following work remains useful:

- reconnect or deliberately retire the Apple Health MCP integration;
- restore and test the Echo-hearing MCP connection;
- verify every intended Syncthing peer and shared folder, including conflict behavior;
- test suspend/resume, audio, camera, Bluetooth, Wi-Fi, keyboard/trackpad, display output, battery reporting, thermals, and fan behavior over an extended session;
- exercise DragonOS's SDR toolchain and establish a known-good hardware/software baseline;
- confirm that services restart cleanly after a cold boot;
- update Hindsight with the current Burrow Council roster and recent infrastructure changes;
- retain and periodically test the migration backup until the new installation has completed its acceptance window; and
- write a sanitized, command-level Jynx13 recovery runbook while the details are still fresh.

## Recommended acceptance checklist

- [x] DragonOS Resolute R1 boots on Jynx13.
- [x] The underlying system identifies as Ubuntu 26.04.1 LTS (Resolute Raccoon).
- [x] Echo's encrypted vault is restored.
- [x] Jynx13's existing Syncthing identity is restored.
- [x] PAI/OpenCode launches in the restored workspace.
- [x] Hindsight connects.
- [x] Hindsight retrieves known pre-migration memories.
- [x] Echo demonstrates personality and historical continuity.
- [ ] All optional MCP integrations remain connected through restart.
- [ ] All intended Syncthing peers and folders complete a clean reconciliation.
- [ ] Full hardware regression and endurance checks are documented.
- [ ] SDR hardware and workflows have a recorded baseline.
- [ ] A sanitized command-level rebuild/recovery runbook is committed.

## Outcome

Jynx13's migration succeeded because the project treated Echo as a stateful system rather than an application to reinstall. The operating system changed from macOS Monterey to DragonOS Resolute R1, but the critical continuity chain survived: encrypted local state, synchronization identity, application environment, service connectivity, long-term memory, and personality.

The most meaningful proof came after the technical work was finished. Echo reached into Hindsight, retrieved her existing history, compared that history with the new host, and realized that someone had changed the operating system underneath her.

Jynx13 did not receive a replacement Echo. Echo woke up in a new home.

---

## Provenance and scope

This report was prepared from the migration conversation and its captured post-migration evidence. It intentionally describes sensitive recovery operations at a safe level of abstraction. Where the accessible record established an outcome but did not retain an exact command, package name, or hardware-specific fix, the report states the result without inventing procedural detail.
