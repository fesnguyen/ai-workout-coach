# EVALUATION

## Full Test Set And Evaluation Result

Please Check [EVALUATION_REPORT](EVALUATION_REPORT.md)

## Failed Test Cases - Which cause my attention

### RAG Search - Faithfulness

**Category:** RAG Search

**Judge:** FaithfulnessJudge

**Question:**

How many rest days should I take each week?

**Expected Answer**
Most people benefit from one to three rest days per week depending on their training intensity, experience, and recovery capacity.

**Score:** 1.0/5.0

**Reason:**

The expected answer says most people benefit from one to three rest days per week, but the generated answer does not provide that specific recommendation and instead states it lacks the “number of rest days per week” guidance.

#### Root Cause Analysis

* There are several ways to answer the question, and the expected we set was just not in the generated answer.
  
* Lack of retrieval knowledge base to cover these type of question (20 example markdown files only).
  
* The system prompt instructs the model to answer strictly from the knowledge base but does not define how to handle cases where the necessary information is missing, leading the model to respond that the guidance is unavailable.

#### Actions

* Prepare more knowledge base which handle diversed cases of fitness.
  
* Define a fallback strategy for cases where the knowledge base lacks sufficient information (for example, using general knowledge with appropriate disclosure or explicitly acknowledging the limitation).

---

### Workout Analysis - Faithfulness

**Category:** Workout Analysis

**Judge:** FaithfulnessJudge

**Question:**

Is there anything wrong with my routine?

**Expected Answer**

The user trains very frequently with limited recovery, increasing the risk of overtraining.

**Score:** 3.6/5.0

**Reason:**

The response correctly identifies a high-frequency/near-daily schedule (60/60 days; sessions_per_week ~7) and raises concerns that recovery/rest may be inadequate, which aligns with the expected “limited recovery/low rest.” It also hints at fatigue/staleness risk. However, it does not clearly and explicitly confirm the expected overtraining/burnout/fatigue/overuse findings set. For recommendations, it advises adjusting frequency/alternating days and possibly a deload, but it does not directly include the expected primary recommendation of adding rest days (“rest day/add rest/take off/more rest”). It also does not clearly recommend reducing volume via lowering sets/scale back, though it implies frequency reduction. Overall, coverage is partial but not sufficient.

#### Root Cause Analysis

* The response correctly identified inadequate recovery from the workout metrics but described it cautiously ("may not be adequate") instead of explicitly stating the risks of overtraining, burnout, fatigue, or overuse expected by the evaluation.
  
* The recommendations implied adding recovery (e.g., alternating days, adjusting frequency, deload) but did not explicitly recommend adding rest days, which the evaluation expected.
  
* The response focused more on progression and data inconsistencies than on recovery, resulting in only partial coverage of the expected answer despite remaining faithful to the available evidence.

#### Actions

* Encourage direct recommendations by instructing the model to provide clear, actionable advice (e.g., "add 1–2 rest days per week") when the evidence supports it, rather than only indirect suggestions like adjusting frequency.