# JustAI Roulette - RSL Club Machine Improvement Plan

## Overview

Transform the current Tkinter roulette app into an authentic Sydney RSL club-style electronic roulette machine experience. RSL club machines are known for their distinctive visual style, ease of use for senior players, and regulated gaming experience.

---

## Phase 1: Visual Identity Overhaul

### 1.1 RSL Machine Color Scheme
**Current:** Dark premium theme with gold accents
**Target:** Authentic RSL machine aesthetic

- **Primary Background:** Deep burgundy/maroon (#4a1c2c) - signature RSL color
- **Secondary:** Rich navy (#1a1f3a) for panels
- **Accent:** Bright gold (#ffd700) for highlights and wins
- **Table Felt:** Classic casino green (#006633) - brighter than current
- **Chrome/Metal:** Silver gradients for machine bezels (#c0c0c0 → #808080)
- **LED Glow:** Neon-style glows on active elements

### 1.2 Machine Frame & Bezels
Add visual elements that simulate a physical machine:

- **Outer Chrome Bezel:** Rounded rectangle frame around entire UI
- **Screen Bezels:** Inset panels with subtle 3D depth
- **Corner Decorations:** RSL-style ornamental corners
- **Brand Bar:** Top banner with "JustAI Roulette" in vintage casino font
- **Machine Number:** Display a mock machine ID (e.g., "MACHINE 07")

### 1.3 Typography Updates
- **Primary Font:** Bold, condensed sans-serif (simulate "Casino" style)
- **Numbers:** Large, high-contrast, easy to read at distance
- **Winning Numbers:** LED-style segmented display font
- **Minimum 16px** base font for accessibility (RSL machines cater to older players)

---

## Phase 2: Wheel & Animation Enhancements

### 2.1 Realistic Wheel Rendering
**Current:** Basic canvas drawing with simple animation
**Target:** RSL-style electronic wheel display

- **3D Depth Effect:** Gradient shading to simulate bowl depth
- **Metallic Frets:** Silver dividers between number pockets
- **Ball Track:** Visible outer track where ball travels
- **Pocket Highlights:** Subtle lighting on winning pocket
- **Ball Reflection:** Shiny metallic ball appearance
- **Shadow Effects:** Drop shadows for depth

### 2.2 Enhanced Spin Animation
- **Realistic Physics:** Ball bounces between pockets before settling
- **Speed Variation:** Fast start, gradual slowdown with "clacking" simulation
- **Multiple Ball Bounces:** 2-3 final bounces before rest
- **Suspense Timing:** Longer slowdown for dramatic effect
- **Result Flash:** Winning number flashes/pulses when determined

### 2.3 Win Celebration Effects
- **Number Glow:** Winning number glows bright gold
- **Particle Effects:** Sparkle/star burst on big wins
- **Screen Flash:** Brief gold overlay flash
- **Progressive Reveal:** Winnings count up visually

---

## Phase 3: Betting Table Improvements

### 3.1 RSL-Style Table Layout
- **Larger Touch Targets:** Minimum 60x60px bet areas (touchscreen friendly)
- **Clearer Boundaries:** White/gold borders on all bet regions
- **Hover States:** Glow effect when hovering over bet area
- **Pressed States:** Visual depression when clicking
- **Bet Confirmation:** Brief flash when bet placed

### 3.2 Enhanced Chip Display
**Current:** Simple circle markers with text
**Target:** Realistic stacked chips

- **3D Chip Stacks:** Show chips stacked when multiple bets
- **Chip Edge Detail:** Striped edges like real chips
- **Shadow:** Drop shadow under chips
- **Stack Limits:** Visual indicator when near max bet
- **Chip Animation:** Chips slide into place when bet

### 3.3 Improved Chip Tray
- **Physical Tray Look:** Curved holder appearance
- **Chip Hover:** Lift effect when hovering
- **Selected Glow:** Bright ring around selected chip
- **Denomination Labels:** Clearer value display
- **Quick-Select:** Larger click targets

---

## Phase 4: Sound Design

### 4.1 Cross-Platform Audio System
**Current:** Windows-only `winsound`
**Target:** Cross-platform audio with pygame or simpleaudio

Required sounds:
- **Chip Place:** Satisfying "clink" when betting
- **Chip Stack:** Multiple clinks for stacking
- **Spin Start:** Ball release sound
- **Ball Rolling:** Continuous rolling loop
- **Ball Bouncing:** Click-clack of ball in pockets
- **Ball Settle:** Final drop sound
- **Win Chime:** Triumphant short jingle
- **Big Win:** Extended celebration fanfare
- **Button Press:** Tactile click feedback
- **Error:** Subtle negative tone
- **Countdown Tick:** Optional tick for last 5 seconds

### 4.2 Ambient Sounds (Optional)
- **Machine Hum:** Low ambient electronic hum
- **Club Ambience:** Distant pokies/chatter (toggleable)

---

## Phase 5: Information Displays

### 5.1 RSL-Style Result Board
**Current:** Simple history chips
**Target:** LED-style electronic display board

- **Marquee Display:** Scrolling last 20 results
- **Color-Coded Columns:** Red/Black/Green columns
- **Hot Numbers Panel:** Flashing "HOT" indicator
- **Cold Numbers Panel:** "COLD" indicator
- **Statistics Bar:** Red/Black percentage with progress bar

### 5.2 Enhanced Stats Panel
- **Streak Tracking:** Current color/parity streak
- **Pattern Display:** Visual pattern recognition
- **Sector Analysis:** Wheel sector hit frequency
- **Session Timer:** How long playing
- **Spin Counter:** Prominent spin number display

### 5.3 Win Display
- **Large LED Numbers:** Winning amount in big LED font
- **Win Type Label:** "STRAIGHT UP WIN!", "COLUMN WIN!", etc.
- **Multiplier Display:** "35x YOUR BET!"
- **Total Won This Session:** Running total

---

## Phase 6: Player Experience Features

### 6.1 Quick Bet Buttons
RSL machines have one-touch betting options:

- **Bet Red/Black:** Single button for even money
- **Bet Odd/Even:** Single button
- **Bet High/Low:** Single button
- **Bet Columns:** Three quick buttons
- **Bet Dozens:** Three quick buttons
- **Repeat Last:** Prominent re-bet button
- **Double Bet:** Double all current bets
- **Favourite Numbers:** Save up to 5 favourite numbers

### 6.2 Bet Templates
- **Lucky Dip:** Random bet placement
- **Full Coverage:** Bet all numbers
- **Neighbours:** Bet number + neighbours on wheel
- **Orphelins/Tiers/Voisins:** European call bets
- **Custom Patterns:** Save custom bet configurations

### 6.3 Auto-Play Enhancements
- **Spin Count Limit:** Stop after X spins
- **Win Limit:** Stop if balance reaches target
- **Loss Limit:** Stop if balance drops below threshold
- **Pattern Betting:** Auto-bet on patterns (e.g., always chase hot numbers)

---

## Phase 7: Responsible Gaming Features

### 7.1 Session Controls (RSL Compliance Style)
- **Session Timer Display:** Prominent time played
- **Break Reminders:** "You've been playing for 30 minutes"
- **Session Limit Setting:** Max time per session
- **Spend Tracking:** Clear total spent this session
- **Reality Check:** Periodic popup with session stats

### 7.2 Limit Settings
- **Loss Limit:** Stop playing at set loss amount
- **Win Goal:** Notification when goal reached
- **Bet Limit:** Maximum single bet (already have max bet)
- **Session Budget:** Set budget before playing

### 7.3 Information Panels
- **Odds Display:** Clear probability for each bet type
- **House Edge Info:** Transparent about 2.7% edge
- **Help Button:** Comprehensive rules and odds
- **Gambling Help:** Link to gambling help resources

---

## Phase 8: Technical Improvements

### 8.1 Code Architecture Refactor
Split `__main__.py` into modules:

```
src/justai_roulette/
├── __main__.py          # Entry point only
├── app.py               # Main application class
├── ui/
│   ├── wheel.py         # Wheel component
│   ├── table.py         # Betting table component
│   ├── chips.py         # Chip tray component
│   ├── stats.py         # Statistics panel
│   ├── controls.py      # Buttons and controls
│   └── theme.py         # Colors, fonts, styling
├── game/
│   ├── engine.py        # Game logic
│   ├── bets.py          # Bet types and payouts
│   └── rng.py           # Random number generation
├── audio/
│   ├── player.py        # Cross-platform audio
│   └── sounds/          # Sound files
├── data/
│   ├── session.py       # Session management
│   └── stats.py         # Statistics tracking
└── utils/
    └── helpers.py       # Utility functions
```

### 8.2 Performance Optimizations
- **Canvas Caching:** Pre-render static elements
- **Efficient Redraws:** Only redraw changed elements
- **Animation Frames:** Consistent 60fps targeting
- **Memory Management:** Clear old canvas items

### 8.3 Configuration System
- **Config File:** JSON/YAML for all settings
- **Theme Presets:** Multiple color schemes
- **Layout Options:** Compact/Standard/Large modes

---

## Phase 9: Additional Game Modes (Future)

### 9.1 American Roulette
- Add 00 pocket option
- Adjusted payouts
- Five-number bet (0, 00, 1, 2, 3)

### 9.2 Multi-Wheel Mode
- Display 2-4 wheels simultaneously
- Bet across multiple wheels
- Combined statistics

### 9.3 Tournament Mode
- Fixed starting balance
- Timed sessions
- Leaderboard tracking

---

## Implementation Priority

### Immediate (High Impact, Lower Effort)
1. Cross-platform audio system
2. Enhanced color scheme (RSL burgundy theme)
3. Improved chip visuals and animations
4. Quick bet buttons
5. Better win celebrations

### Short-term (High Impact, Medium Effort)
6. Machine frame/bezel visual elements
7. LED-style result display board
8. Enhanced spin animation (ball bouncing)
9. Sound effects library
10. Responsible gaming features

### Medium-term (Medium Impact, Higher Effort)
11. Code architecture refactor
12. 3D wheel effects
13. Bet templates system
14. Advanced statistics
15. Accessibility improvements

### Long-term (Future Enhancements)
16. American roulette mode
17. Custom themes
18. Tournament mode
19. Network multiplayer (shared wheel)

---

## Success Metrics

- **Visual Authenticity:** Looks like a real RSL machine
- **Ease of Use:** Playable with minimal learning curve
- **Performance:** Smooth 60fps animations
- **Accessibility:** Readable for older players
- **Engagement:** Satisfying sound and visual feedback
- **Responsibility:** Clear session tracking and limits

---

## Notes on RSL Machine Characteristics

Sydney RSL club machines typically feature:
- Burgundy/maroon and gold color scheme
- Large, easy-to-read displays
- Touch-screen optimized interfaces
- Clear betting area boundaries
- Prominent balance and bet displays
- Session tracking and responsible gaming features
- "No Frills" practical design over flashy effects
- Reliability over novelty

The goal is to capture this authentic feel while maintaining the premium dark theme aesthetic where appropriate.
