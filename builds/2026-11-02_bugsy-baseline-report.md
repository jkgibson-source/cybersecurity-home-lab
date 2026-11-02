# Operation Bugsy Baseline: pre- and post-bridge network comparison

**Report date:** November 2, 2026
**Design:** Two consecutive overnight observational monitoring sessions, one before and one after the network bridge installation.
**Verdict:** The reported Wi-Fi signal score improved substantially, and typical Talon response times improved modestly. These logs do **not** demonstrate improved end-to-end reliability: post-bridge Internet latency was higher, both targets recorded more failed probes, and a shared failure streak occurred.
**Operator observation:** In day-to-day use since installation, the practical experience has been markedly better than the prior state. The added Internet latency (about 6 ms) has been imperceptible, and I have experienced no dropouts or breaks in service during active use. This is a firsthand, qualitative assessment rather than a measured result; the one logged shared interruption (08:50 UTC, 03:50 EST) occurred overnight, outside active use, during a period of recent storm activity in South Florida, when brief power or utility service interruptions are common.

## 1. Executive findings

- **Signal score:** 52/100 in every pre-bridge row versus 100/100 in every post-bridge row: **+48 score points**. This is a relative interface score, not dBm, bandwidth, or a physical doubling of radio strength.
- **Typical local response:** Talon median RTT fell from **3.30 to 3.08 ms** (−0.22 ms; −6.7%), and p95 fell from **5.038 to 4.194 ms** (−16.8%). However, the mean change was small and uncertain when temporal clustering was considered.
- **Internet response:** Mean RTT rose from **8.947 to 15.225 ms**, a **+6.278 ms / +70.2%** increase. The median rose from **8.72 to 14.80 ms**. This shift persists after excluding partial hours and across block sizes.
- **Failures:** Talon failed probes increased from **1/10,246 to 5/10,118**; Internet failed probes increased from **0/10,246 to 5/10,118**. These are sparse events, including a cluster, so they cannot establish a general long-run failure-rate change.
- **Interruption evidence:** Four consecutive post-bridge rows reported failure for both targets. This is a meaningful observed interruption, but five-second sampling cannot measure its exact duration or identify its cause.
- **Interpretation:** Bugsy achieved the observed signal-score objective. Broader claims that it eliminated dropouts, reduced Internet latency, or improved overall reliability would exceed the evidence.

## 2. Inputs, chronology, and measurement scope

The session dated `20261031_230702` is treated as **pre-bridge** and `20261101_220817` as **post-bridge**. The CSVs themselves do not contain an installation marker or a topology record. Talon was also relocated into the Burrow during this period, so this comparison evaluates the overall before/after configuration, not the bridge in isolation.

Analysis uses the four original CSV files listed in Section 10.

| Coverage | Pre-bridge | Post-bridge |
|---|---|---|
| First row (UTC) | 2026-11-01 03:07:02.502621+00:00 | 2026-11-02 03:08:17.015631+00:00 |
| Last row (UTC) | 2026-11-01 17:20:48.735596+00:00 | 2026-11-02 17:11:23.247619+00:00 |
| First-to-last elapsed time | 14.2295 h | 14.0517 h |
| Raw rows / probes per target | 10,246 | 10,118 |
| Hourly summary rows | 15 | 15 |
| Complete UTC hours | 13 (04:00–16:59) | 13 (04:00–16:59) |
| SSID in every row | Same home 5 GHz network | Same home 5 GHz network |

The first run begins October 31 at 23:07 EDT and ends November 1 at 12:20 EST. The second begins November 1 at 22:08 EST and ends November 2 at 12:11 EST. The first run crosses the fall daylight-saving transition: its local clock repeats an hour. All chronology, grouping, and cadence checks therefore use the explicit **UTC** timestamps. Matching UTC hour of day does not fully match local civil time across that transition.

The shorter post session has 128 fewer observations, approximately 1.25% less exposure. Counts are accompanied by denominators; aggregate means are computed from raw successful observations, rather than averaging rounded hourly averages. Hourly files summarize the same observations and are not independent replication.

`talon_ok` and `internet_ok` are analyzed as recorded binary probe outcomes. "Loss" below means **failed logged probes**, not a verified packet-level capture loss rate. Probe commands, destinations, timeout settings, payload sizes, interface counters, and bridge configuration are absent from these four files. RTT results are conditional on success; a timeout is not imputed as zero or as an invented RTT.

## 3. Data quality and reconciliation

- Both raw files contain unique, increasing UTC timestamps. No interval exceeds 7.5 seconds; neither run shows a missing five-second sampling slot under that criterion.
  - Pre interval minimum / median / maximum: **4.999812 / 5.000117 / 5.002910 seconds**.
  - Post interval minimum / median / maximum: **4.999986 / 5.000119 / 5.003819 seconds**.
- Blank RTT cells correspond exactly to failed probes: 1 Talon / 0 Internet pre, and 5 Talon / 5 Internet post. There are no mismatches between a failure flag and an empty RTT.
- All 30 hourly rows reconcile to raw UTC-hour groups: sample counts and consecutive-failure maxima match exactly; loss percentages, successful RTT averages, and RTT maxima agree within **0.00501** of the stored values (rounding tolerance).
- Hourly sample totals match raw totals exactly: **10,246 pre / 10,118 post**. Partial first and last hours are retained for whole-session descriptions and excluded from the primary uncertainty comparison.
- An uninterrupted logger does not prove an uninterrupted network. Stable SSID and score fields do not identify the access point, route, or upstream link state.

## 4. Latency: typical performance and tails

Values are milliseconds and include only successful target probes. Percentiles use linear interpolation between ordered observations (NumPy default). Changes are post minus pre.

| Target / metric | Pre | Post | Change |
|---|---:|---:|---:|
| Talon Mean | 3.618 | 3.504 | -0.114 |
| Talon Median | 3.300 | 3.080 | -0.220 |
| Talon p90 | 4.400 | 3.750 | -0.650 |
| Talon p95 | 5.038 | 4.194 | -0.844 |
| Talon p99 | 7.450 | 5.736 | -1.714 |
| Talon Maximum | 286.000 | 730.000 | +444.000 |
| Talon Sample SD | 4.205 | 13.199 | +8.994 |
| Internet Mean | 8.947 | 15.225 | +6.278 |
| Internet Median | 8.720 | 14.800 | +6.080 |
| Internet p90 | 10.700 | 19.200 | +8.500 |
| Internet p95 | 11.300 | 20.100 | +8.800 |
| Internet p99 | 13.400 | 22.488 | +9.088 |
| Internet Maximum | 298.000 | 876.000 | +578.000 |
| Internet Sample SD | 5.147 | 13.750 | +8.603 |

Talon's median and upper ordinary percentiles improve, but its largest successful RTT increases from 286 to 730 ms and its standard deviation increases substantially. A better typical RTT can coexist with worse rare spikes. Internet RTT shifts upward throughout the distribution, rather than only at its maximum.

### Threshold exceedances

Thresholds are descriptive choices, not application-specific service requirements. Denominators are successful probes; failed probes are reported separately.

| Target | Successful probes, pre / post | >20 ms, pre / post | >50 ms, pre / post | >100 ms, pre / post |
|---|---:|---:|---:|---:|
| Talon | 10,245 / 10,113 | 18 / 11 | 7 / 9 | 5 / 8 |
| Internet | 10,246 / 10,113 | 20 / 530 | 10 / 25 | 7 / 11 |

Internet >20 ms observations increase from **0.195% to 5.241%** of successful probes. Talon >20 ms observations decrease, while its >100 ms count increases. No single mean or threshold adequately describes both ordinary response and tail behavior.

## 5. Failures and interruption evidence

| Target / phase | Failed / total | Observed failure rate | Nominal 95% Wilson interval |
|---|---:|---:|---:|
| Talon / Pre | 1 / 10,246 | 0.00976% | 0.00172%–0.05527% |
| Talon / Post | 5 / 10,118 | 0.04942% | 0.02111%–0.11564% |
| Internet / Pre | 0 / 10,246 | 0.00000% | 0.00000%–0.03748% |
| Internet / Post | 5 / 10,118 | 0.04942% | 0.02111%–0.11564% |

Talon's observed rate increases by **0.03966 percentage points**; Internet's by **0.04942 percentage points**. A relative Internet-loss increase is undefined because its pre count is zero. Talon's roughly fivefold sample rate ratio is unstable with so few events and should not be a headline.

The Wilson intervals are a **binomial reference calculation**, not dependence-adjusted uncertainty estimates. The shared four-row failure cluster violates independent-trial assumptions. Do not infer significance from these intervals or their overlap. Zero observed pre Internet failures does not establish a true zero failure probability. With only two sessions and a handful of events, a reliable long-run or causal loss comparison is unavailable.

### Event log (UTC)

| Session | Target(s) | Failed row timestamps | Longest run |
|---|---|---|---:|
| Pre | Talon only | 2026-11-01 11:45:53.248399 | 1 |
| Post | Talon only | 2026-11-02 03:52:27.081339 | 1 |
| Post | Internet only | 2026-11-02 05:36:17.230177 | 1 |
| Post | Both | 2026-11-02 08:50:37.512703, 08:50:42.512827, 08:50:47.512907, 08:50:52.513034 | 4 |

Talon has one pre failure run and two post runs; Internet has no pre failure runs and two post runs. Four rows fail jointly post; no pre row fails jointly. The union of failed-target rows is **1 pre / 6 post**, not 1 / 10: summing target failures double-counts the shared event.

The four-row streak spans approximately **15 seconds between its first and last recorded timestamps**, often summarized operationally as about 20 seconds of failed sampling slots. Neither figure is a measured continuous outage duration. Actual probe execution and timeout timing are unknown, and success between samples cannot be ruled out. Joint row failures suggest a shared disruption along the monitored paths, but do not distinguish Wi-Fi, bridge/backhaul, router, host scheduling, a brief power fluctuation (storms were active in the area during this period), or other causes. A successful Internet probe alongside a failed Talon probe also cautions against equating every target failure with total Internet loss.

## 6. Statistical comparison that respects time structure

Five-second rows are not 10,000 independent experiments per phase. Successful-observation lag-one RTT correlations are approximately **0.37/0.38 for Talon** and **0.24/0.27 for Internet** (pre/post). These diagnostics omit failures and are descriptive. They support avoiding a naive per-row t-test.

The primary comparison uses the **13 complete UTC hours, 04:00 through 16:59**, common to both days. Within each hour and target, compute the mean successful RTT; pair hours by UTC time of day; subtract pre from post; resample the 13 paired differences with replacement **20,000 times** and take the 2.5th/97.5th percentiles. Each complete hour has equal weight. The displayed intervals are exploratory paired-block bootstrap intervals for the sampled overnight windows.

| Block size | Paired blocks | Talon mean change (95% interval), ms | Internet mean change (95% interval), ms |
|---|---:|---:|---:|
| 15 min | 55 | -0.100 (-0.572, +0.550) | +6.276 (+5.815, +6.780) |
| 30 min | 27 | -0.096 (-0.581, +0.562) | +6.281 (+5.927, +6.757) |
| 60 min | 13 | -0.088 (-0.606, +0.586) | +6.295 (+5.936, +6.781) |

For the primary 60-minute comparison, Talon hourly means average **3.621 pre / 3.532 post ms**, while Internet hourly means average **8.950 pre / 15.245 post ms**. Internet mean RTT is higher in **all 13 matched complete hours**. Talon mean RTT is lower in 11 of the 13, but rare spikes make its mean-change interval include zero.

Sensitivity calculations use non-overlapping UTC-aligned 15- and 30-minute bins, retaining a bin only if each session has at least `12 × minutes − 2` rows. There are 55 and 27 matched bins respectively. Random generator: NumPy `default_rng(20261102)`, iterating block sizes 15, 30, 60 and targets Talon, Internet. The direction of the Internet shift is consistent across these choices; evidence for a reduced Talon **mean** is inconclusive. Median and percentile changes remain descriptive, without separate inferential claims.

**Limits of these intervals:** Hour blocks can remain dependent, and 13 blocks is a small sample. Resampling hours within one night per condition cannot measure variation across independent nights. UTC matching controls the sampled UTC window, not traffic, local clock time, routing, day of week, or workload. These intervals are not proof that the bridge caused either change, nor prediction intervals for future operation. No multiple-metric significance claims or failure-rate hypothesis tests are made.

## 7. Hourly detail

These are the supplied rounded hourly summaries; hours are UTC. First and last rows are partial. Global results above are independently computed from raw data.

| UTC hour of day | Samples pre / post | Talon failures pre / post | Internet failures pre / post | Talon mean pre / post, ms | Internet mean pre / post, ms |
|---|---:|---:|---:|---:|---:|
| 03:00 | 636 / 621 | 0 / 1 | 0 / 0 | 3.53 / 3.18 | 8.89 / 14.88 |
| 04:00 | 720 / 720 | 0 / 0 | 0 / 0 | 3.44 / 3.18 | 8.75 / 14.86 |
| 05:00 | 720 / 720 | 0 / 0 | 0 / 1 | 3.42 / 6.69 | 8.75 / 17.37 |
| 06:00 | 720 / 720 | 0 / 0 | 0 / 0 | 3.45 / 3.12 | 8.98 / 14.65 |
| 07:00 | 720 / 720 | 0 / 0 | 0 / 0 | 3.33 / 3.17 | 8.73 / 15.16 |
| 08:00 | 720 / 720 | 0 / 4 | 0 / 4 | 3.43 / 4.41 | 8.74 / 16.03 |
| 09:00 | 720 / 720 | 0 / 0 | 0 / 0 | 3.39 / 3.19 | 8.73 / 14.82 |
| 10:00 | 720 / 720 | 0 / 0 | 0 / 0 | 3.42 / 3.13 | 8.7 / 14.84 |
| 11:00 | 720 / 720 | 1 / 0 | 0 / 0 | 4.94 / 3.15 | 10.37 / 16.17 |
| 12:00 | 720 / 720 | 0 / 0 | 0 / 0 | 3.59 / 3.23 | 8.98 / 15.36 |
| 13:00 | 720 / 720 | 0 / 0 | 0 / 0 | 3.65 / 3.16 | 8.88 / 14.78 |
| 14:00 | 720 / 720 | 0 / 0 | 0 / 0 | 3.87 / 3.16 | 9.06 / 14.94 |
| 15:00 | 720 / 720 | 0 / 0 | 0 / 0 | 3.58 / 3.15 | 8.81 / 14.45 |
| 16:00 | 720 / 720 | 0 / 0 | 0 / 0 | 3.58 / 3.18 | 8.86 / 14.76 |
| 17:00 | 250 / 137 | 0 / 0 | 0 / 0 | 3.73 / 3.09 | 8.97 / 15.45 |

Failure counts in this table recover the integer counts from rounded hourly percentages and agree with the raw event log. Pre rows refer to November 1; post rows refer to November 2.

## 8. What the experiment establishes, and what remains open

| Question | Finding |
|---|---|
| Did the reported signal score increase? | Yes: constant 52 → constant 100 in the recorded sessions. |
| Did ordinary Talon response improve? | Yes descriptively: lower median, p95, and p99. Mean improvement is uncertain in the block analysis. |
| Did Internet response improve? | No: observed RTT is higher across ordinary percentiles and all complete-hour means. |
| Were dropouts eliminated? | No: post failures include a shared four-row streak. |
| Was reliability proven worse in general? | No: observed failures are worse, but rare clustered events in two sessions cannot establish the long-run rate. |
| Did throughput improve? | Unknown: no throughput, retransmission, or application performance measurements. |
| Is Bugsy the cause of the changes? | Unresolved: intervention, day, topology, routing, traffic, and environment are confounded. |

Additional cautions: an unchanged SSID does not prove an unchanged access point or path; a constant signal score may reflect quantization, saturation, or reporting behavior; RTT to a single unidentified Internet destination cannot represent all Internet services. The source code and topology documentation should be consulted before assigning network-layer causes. The small absolute typical Talon improvement and approximately 6 ms Internet increase may have different practical importance for different applications.

## 9. Recommended follow-up

1. Repeat several comparable overnight sessions per configuration, preferably alternating configuration order where practical. Treat nights as the replication unit; preserve date, traffic conditions, endpoint addresses, and configuration changes.
2. Record the probe command, timeout, packet size, actual send/completion times, BSSID, frequency/channel, interface, route, and bridge/backhaul status. Keep UTC as the canonical clock.
3. Probe the local access point/router, both sides of the bridge, and more than one stable Internet target to help locate shared disruptions. Collect relevant host/router logs around **2026-11-02 08:50 UTC**, including device uptime and any UPS or power-event records, to check whether a brief power interruption explains the shared failure.
4. Measure throughput separately under controlled load and log retransmissions or application interruptions if those are operational goals. Signal score alone cannot answer those questions.
5. Define practical acceptance thresholds before the next run: permitted failure rate, maximum failure streak, RTT percentiles, and application requirements. Compare all attempted probes for reliability and successful probes for latency.

## 10. Provenance and reproducibility

Raw CSVs are the authoritative observations; hourly CSVs are cross-checks. Arithmetic uses unrounded raw RTT values; reporting precision does not imply corresponding measurement accuracy. Sample SD uses `ddof=1`; nominal Wilson intervals use z = 1.95996398454. Failure rate = failed rows / all rows for that target. Whole-session mean = sum of successful RTT / successful count. Threshold comparisons are strictly greater than the stated value. No outlier removal, timeout imputation, or silent trimming is applied to whole-session results.

The table below identifies the exact analyzed inputs. Hashes are for the original, unredacted files; any published copies have the SSID field redacted and will hash differently.

| Input | Bytes | SHA-256 |
|---|---:|---|
| `bugsy_20261031_230702_hourly.csv` | 1,047 | `d8c1abde54d58d1763c338e36eef5a9c4cbdf3ef4adae598350b9bbeb4d342fe` |
| `bugsy_20261031_230702_raw.csv` | 961,392 | `dcda8a129bbd957c7121b9d78416e82884e05a9fd61d2c6bbf1840e787a066de` |
| `bugsy_20261101_220817_hourly.csv` | 1,068 | `faf2f4dbe3ed57c3b48b71ee7837dc278e4c992db2535373840a33f267be58a0` |
| `bugsy_20261101_220817_raw.csv` | 960,129 | `400818dddd63b49fc80fe848fea2c786694f41f507106c26e67888a4744208f4` |
