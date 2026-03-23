# Product Specification

## 1. Product Overview

### 1.1 Product Name
**English Speaking Trainer** - Professional English Speaking Practice Platform

### 1.2 Product Vision
Empower professionals to master English speaking skills through AI-powered, scenario-based conversation practice, enabling confident communication in real-world professional situations.

### 1.3 Product Goals

| Goal | Description | Success Metric |
|------|-------------|----------------|
| Skill Improvement | Help users improve English speaking proficiency | 80% users show measurable improvement in 30 days |
| Scenario Mastery | Enable confident communication in professional contexts | 90% scenario completion rate |
| Engagement | Create engaging, immersive learning experience | 60% weekly retention rate |
| Monetization | Build sustainable revenue model | 15% free-to-paid conversion |

---

## 2. User Personas

### 2.1 Primary Persona: Professional Learner

| Attribute | Description |
|-----------|-------------|
| **Name** | Zhang Wei |
| **Age** | 28-40 |
| **Occupation** | Engineer / Manager / Sales Professional |
| **English Level** | Intermediate (CEFR B1-B2) |
| **Pain Points** | - Limited speaking practice opportunities<br>- Nervous in professional English conversations<br>- Cannot find relevant practice scenarios |
| **Goals** | - Confidently present products at international exhibitions<br>- Discuss technical topics with foreign colleagues<br>- Handle business negotiations professionally |
| **Usage Pattern** | 15-30 minutes daily practice during commute or lunch break |

### 2.2 Secondary Persona: Career Advancer

| Attribute | Description |
|-----------|-------------|
| **Name** | Li Ming |
| **Age** | 25-35 |
| **Occupation** | Job seeker / Career changer |
| **English Level** | Upper-intermediate (CEFR B2-C1) |
| **Pain Points** | - Need to prepare for English interviews<br>- Want to improve specific professional vocabulary<br>- Limited budget for language courses |
| **Goals** | - Pass English job interviews<br>- Improve industry-specific terminology |
| **Usage Pattern** | Intensive practice before interviews |

---

## 3. Core Features

### 3.1 Feature Matrix

| Feature | Description | Priority | MVP |
|---------|-------------|----------|-----|
| **Scenario Selection** | Browse and select practice scenarios by category | P0 | Yes |
| **AI Dialogue Generation** | Generate contextual dialogues using LLM | P0 | Yes |
| **Text-to-Speech Playback** | Convert dialogue text to natural speech | P0 | Yes |
| **Role-Play Practice** | User plays one role, AI plays the other | P0 | Yes |
| **Speech Recording** | Record user speech during practice | P0 | Yes |
| **Basic Pronunciation Evaluation** | Overall pronunciation scoring | P0 | Yes |
| **User Authentication** | Sign up, login, profile management | P0 | Yes |
| **Practice History** | View past practice sessions | P1 | Yes |
| **Learning Reports** | Weekly/monthly progress reports | P1 | No |
| **Advanced Evaluation** | Word-level and phoneme-level feedback | P2 | No |
| **Custom Scenario Generation** | User-defined scenario creation | P2 | No |
| **Payment System** | Subscription and one-time purchases | P2 | No |

### 3.2 Feature Details

#### 3.2.1 Scenario Selection
- Categories: Exhibition, Technical Discussion, Business, Daily Life
- Each scenario includes: title, description, difficulty level, estimated duration
- Free scenarios: 5 per category
- Premium scenarios: Unlimited with subscription

#### 3.2.2 AI Dialogue Generation
- Context-aware dialogue generation
- Role assignment: User role vs. AI role
- Dialogue structure: Opening → Main conversation → Closing
- Support for follow-up questions and variations

#### 3.2.3 Text-to-Speech Playback
- Natural-sounding voice synthesis
- Multiple voice options (male/female, accents)
- Adjustable playback speed
- Sentence-by-sentence highlighting

#### 3.2.4 Role-Play Practice
- Interactive conversation flow
- Real-time AI responses
- Option to replay AI speech
- Pause and resume functionality

#### 3.2.5 Speech Pronunciation Evaluation
- Overall score (0-100)
- Accuracy, fluency, completeness metrics
- Visual feedback with color coding
- Detailed feedback for improvement

---

## 4. MVP Scope

### 4.1 MVP Features (Phase 1)

```
┌─────────────────────────────────────────────────────────┐
│                    MVP Feature Set                       │
├─────────────────────────────────────────────────────────┤
│  ✅ User Registration & Login                           │
│  ✅ Scenario Browsing (20 free scenarios)               │
│  ✅ AI Dialogue Generation                              │
│  ✅ TTS Audio Playback                                  │
│  ✅ Role-Play Practice Mode                             │
│  ✅ Basic Pronunciation Evaluation                      │
│  ✅ Practice History (last 10 sessions)                 │
│  ❌ Advanced Evaluation (Premium)                       │
│  ❌ Custom Scenarios (Premium)                          │
│  ❌ Learning Reports                                    │
│  ❌ Payment System                                      │
└─────────────────────────────────────────────────────────┘
```

### 4.2 MVP Success Criteria

| Metric | Target |
|--------|--------|
| App Store Rating | ≥ 4.0 |
| Day-7 Retention | ≥ 30% |
| Average Session Duration | ≥ 10 minutes |
| Scenario Completion Rate | ≥ 70% |
| Crash-free Rate | ≥ 99% |

---

## 5. User Journey

### 5.1 New User Onboarding Flow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Download   │───▶│   Sign Up    │───▶│   Select     │
│     App      │    │   /Login     │    │   Interest   │
└──────────────┘    └──────────────┘    └──────────────┘
                                               │
                                               ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Practice   │◀───│   Tutorial   │◀───│   English    │
│   First      │    │   Walkthrough│    │   Level Test │
│   Scenario   │    │              │    │   (Optional) │
└──────────────┘    └──────────────┘    └──────────────┘
```

### 5.2 Core Practice Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      Practice Session Flow                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Select  │────▶│  Review  │────▶│  Start   │────▶│   AI     │
│ Scenario │     │ Dialogue │     │ Practice │     │  Speaks  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                                          │
      ┌───────────────────────────────────────────────────┘
      ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │────▶│   AI     │────▶│  End     │────▶│  View    │
│  Speaks  │     │ Response │     │ Session  │     │  Report  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
      │                │
      │                │
      ▼                ▼
┌──────────────────────────────────┐
│     Loop until dialogue ends     │
│  (typically 5-10 exchanges)      │
└──────────────────────────────────┘
```

### 5.3 Detailed Practice Flow

```
User Action                    System Response
─────────────────────────────────────────────────────────────────
1. Select Scenario        →   Load scenario details
                             → Generate/Retrieve dialogue
                             
2. Review Dialogue        →   Display full dialogue text
                             → Show role assignments
                             → Play preview audio (optional)
                             
3. Start Practice         →   Initialize session
                             → Begin role-play mode
                             
4. AI Speaks              →   TTS generates audio
                             → Display text with highlight
                             → Wait for user response
                             
5. User Speaks            →   Record audio (max 60s)
                             → STT transcribes speech
                             → Evaluate pronunciation
                             → Display score + feedback
                             
6. AI Response            →   LLM generates contextual response
                             → TTS converts to audio
                             → Continue conversation
                             
7. Session End            →   Calculate overall scores
                             → Store session data
                             → Display summary report
                             → Suggest next scenarios
```

---

## 6. Monetization Strategy

### 6.1 Pricing Tiers

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | - 5 scenarios per category<br>- Basic pronunciation evaluation<br>- 10 practice sessions/week<br>- Practice history (7 days) |
| **Premium Monthly** | $9.99/month | - Unlimited scenarios<br>- Advanced evaluation (word/phoneme level)<br>- Unlimited practice sessions<br>- Custom scenario generation (3/month)<br>- Full practice history<br>- Learning reports |
| **Premium Annual** | $79.99/year | All Premium features +<br>- Priority support<br>- Early access to new features<br>- Custom scenario generation (10/month) |

### 6.2 Revenue Projections

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Total Users | 50,000 | 200,000 | 500,000 |
| Paid Users | 5,000 | 30,000 | 100,000 |
| Conversion Rate | 10% | 15% | 20% |
| Monthly Revenue | $50K | $300K | $1M |

### 6.3 Premium Feature Gates

```
┌─────────────────────────────────────────────────────────┐
│                  Premium Feature Gates                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Free Tier                    Premium Tier               │
│  ─────────                    ─────────────              │
│  Basic scenarios              All scenarios              │
│  Overall score only           Word-level analysis        │
│  Limited sessions             Unlimited sessions         │
│  Standard TTS voices          Premium voices             │
│  No custom scenarios          Custom scenario creation    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Success Metrics & KPIs

### 7.1 Product Metrics

| Category | Metric | Target | Measurement |
|----------|--------|--------|-------------|
| Acquisition | Daily Active Users (DAU) | 10K by M6 | Analytics |
| Acquisition | App Store Downloads | 100K by M12 | Store data |
| Engagement | Session Duration | >10 min | Analytics |
| Engagement | Scenarios Completed/Week | >3 | Database |
| Retention | Day-1 Retention | >40% | Analytics |
| Retention | Day-7 Retention | >25% | Analytics |
| Retention | Day-30 Retention | >15% | Analytics |
| Revenue | Free-to-Paid Conversion | >10% | Payment data |
| Revenue | Monthly Recurring Revenue | $50K by M12 | Payment data |

### 7.2 Learning Effectiveness Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Pronunciation Score Improvement | Average score increase over 30 days | +15 points |
| Scenario Mastery Rate | Users completing all dialogue exchanges | >80% |
| Vocabulary Acquisition | New words learned per week | 20 words |
| User Self-Reported Confidence | Survey score (1-5) | >4.0 |

---

## 8. Roadmap

### 8.1 Phase Timeline

```
Phase 1: MVP (Month 1-3)
├── Core practice features
├── Basic evaluation
├── 20 free scenarios
└── User authentication

Phase 2: Premium Features (Month 4-6)
├── Advanced evaluation
├── Payment integration
├── Custom scenario generation
└── Learning reports

Phase 3: Scale (Month 7-12)
├── Multi-language support
├── Social features
├── Enterprise version
└── API for third-party integration

Phase 4: Expansion (Year 2+)
├── B2B offering
├── White-label solution
├── Advanced AI features
└── Global market expansion
```

---

## 9. Non-Functional Requirements

### 9.1 Performance Requirements

| Requirement | Target |
|-------------|--------|
| App Launch Time | <3 seconds |
| API Response Time | <500ms (p95) |
| TTS Generation | <2 seconds per sentence |
| Speech Recognition | <3 seconds |
| Audio Latency | <100ms |

### 9.2 Availability Requirements

| Requirement | Target |
|-------------|--------|
| Uptime | 99.9% |
| Data Backup | Daily |
| Disaster Recovery | <4 hours RTO |

### 9.3 Scalability Requirements

| Requirement | Target |
|-------------|--------|
| Concurrent Users | 10,000 |
| API Requests/Second | 1,000 |
| Storage per User | 100MB |
| Total Storage | 10TB |

---

## 10. Constraints & Assumptions

### 10.1 Technical Constraints
- Mobile-first design (iOS and Android)
- Requires internet connection for AI features
- Minimum iOS 14.0, Android 8.0
- Backend deployed on cloud infrastructure

### 10.2 Business Constraints
- Initial launch in China market
- Chinese and English language support
- Compliance with local data protection regulations
- Third-party AI service dependencies

### 10.3 Assumptions
- Users have intermediate English reading ability
- Users have access to quiet practice environments
- Stable internet connection available
- Users willing to practice 15+ minutes per session
