# 🛡️ Wazuh Deployment & RBAC Hardening Case Study

### Author
J K Gibson  

### Environment
- Docker-based Wazuh (Single Node)
- macOS host (home lab)
- Internal network deployment

---

## 🎯 Objective

Deploy a fully functional Wazuh SIEM in a Docker environment and replace insecure default credentials with a properly configured role-based access control (RBAC) model using a named administrative user.

---

## 🧱 Initial Conditions

- Wazuh deployed via Docker (`single-node`)
- Dashboard accessible at `https://<lab-ip>`
- Default credentials in use:
  - `admin / SecretPassword`
- No custom users configured
- No RBAC customization performed

---

## ⚠️ Problem Summary

During initial hardening attempts, multiple failures occurred:

| Issue | Symptom |
|------|--------|
| Memory mapping misconfiguration | Indexer instability |
| Dashboard errors | `ResponseError`, dashboard not ready |
| Password change failures | `sudo package is not installed` |
| Authentication failures | `kibanaserver` login errors |
| UI errors | `getPatternList` failure |
| Role mapping failures | `Forbidden` errors |

---

## 🔍 Investigation & Root Cause Analysis

### 1. Docker Environment Limitations

Attempting to change passwords via:

```bash
wazuh-passwords-tool.sh
```

Resulted in:

```text
sudo package is not installed
```

**Root Cause:**
- Wazuh container does not include `sudo`
- Tool expects full OS environment, not containerized runtime

---

### 2. Authentication Failures Between Services

Logs showed:

```text
Authentication finally failed for kibanaserver
```

**Root Cause:**
- Credential mismatch between:
  - Wazuh Dashboard
  - Wazuh Indexer (OpenSearch)

---

### 3. UI Failure During User Creation

Error observed:

```text
Error pattern Handler (getPatternList)
```

**Root Cause:**
- User was created without backend roles
- Dashboard attempted to load permissions and failed

---

### 4. RBAC Misunderstanding

Initial approach attempted:

- Direct modification of `all_access` role
- Assigning permissions via UI mapping

Result:

```text
Forbidden
```

---

## 🧠 Critical Insight

OpenSearch/Wazuh RBAC follows this structure:

```
User → Backend Role → Role Mapping → Permissions
```

Key discovery:

- `all_access` is a **reserved role**
- Reserved roles **cannot be modified via UI**
- Proper access must be granted via **backend roles**

---

## ✅ Resolution

### Step 1 — Create Named User

- Navigate:
  Security → Internal Users
- Create user:
  JBird13

---

### Step 2 — Assign Backend Role

Instead of modifying `all_access`, assign:

```
admin
```

to the user under Backend roles

---

### Step 3 — Validate Role Mapping

Confirmed via API:

```bash
curl -k -u admin:SecretPassword https://<IP>:9200/_plugins/_security/api/rolesmapping/all_access
```

Result:

```json
"backend_roles": ["admin"]
```

---

### Step 4 — Authentication Validation

- Logged out of default admin
- Logged in as:
  JBird13

✅ Full administrative access confirmed

---

## 🔐 Security Outcome

| Control | Status |
|--------|-------|
| Named admin user | ✅ Implemented |
| RBAC model | ✅ Correctly configured |
| Default admin usage | ⚠️ Limited (break-glass only) |
| System stability | ✅ Restored |

---

## ⚠️ Remaining Risk

- Default credentials still active:
  admin / SecretPassword

**Mitigation Plan:**
- Rotate credentials using Docker-safe method
- Restrict usage to emergency access only

---

## 📈 Key Lessons Learned

- Reserved roles (`all_access`) cannot be modified directly
- Backend roles drive permission inheritance
- Docker environments may break traditional tooling
- Authentication dependencies between services are tightly coupled
- UI errors can indicate permission misconfiguration, not system failure

---

## 🚀 Impact

This exercise transformed the environment from:

> Default, insecure deployment

to:

> Structured, role-based access-controlled SIEM platform

---

## 🧩 Next Steps

- Harden default admin account
- Create analyst and detection roles
- Begin attack simulation and detection validation
- Map detections to MITRE ATT&CK

---

## 💡 Key Takeaway

> In Wazuh/OpenSearch, permissions are not assigned directly to users — they are inherited through backend roles and mappings. Understanding this model is critical to secure deployment.

---

**End of Case Study**
