# Part 3: Interactive Visualization Tool

## Overview
Build a web-based interactive tool that allows users to explore schools, adjust scoring weights in real-time, compare options, and visualize commute routes.

## Technology Stack

### Frontend Framework Options:
**Recommendation: React + Vite**
- Modern, fast development
- Rich ecosystem
- Good TypeScript support
- Excellent component libraries

**Alternative: Svelte**
- Simpler, less boilerplate
- Great performance
- Smaller bundle size

### Key Libraries:
- **UI Components**: Shadcn/ui or Material-UI
- **Tables**: TanStack Table (React Table v8)
- **Charts**: Recharts or Chart.js
- **Maps**: Leaflet or Google Maps API
- **State Management**: Zustand or React Context
- **Styling**: Tailwind CSS

## Core Features

### 1. School Table View
**Main interactive table with:**
- All schools listed with key info
- Sortable columns (name, score, distance, type)
- Filterable by:
  - City (Amsterdam, Amstelveen)
  - School type (VWO-only, Gymnasium, HAVO+VWO, etc.)
  - Distance range (slider)
  - Score range (slider)
  - Religious affiliation
  - Special programs
- Expandable rows showing detailed info
- Color-coded scores (red/yellow/green)
- Search box for school names

**Columns:**
1. Rank
2. School Name
3. Total Score (with badge)
4. City
5. Type (tags for VWO, HAVO, etc.)
6. Distance
7. Bike Time
8. Quick actions (View Details, Compare)

### 2. Weight Adjustment Panel
**Interactive sliders for criteria weights:**

```
Academic Performance    [====|====] 25%
Location & Access       [===|=====] 15%
Facilities             [==|======] 10%
Student Support        [===|=====] 15%
Environment            [===|=====] 15%
Reviews                [==|======] 10%
Extracurricular        [=|=======]  5%
Practical              [=|=======]  5%
                                  ----
                       Total: 100%
```

**Features:**
- Sliders update scores in real-time
- Total must equal 100% (auto-adjust other weights proportionally)
- Preset profiles:
  - Default (balanced)
  - Academic Focus (high academic, low other)
  - Proximity Focus (high location, lower academic)
  - Well-Rounded (even distribution)
  - Save custom profiles
- Reset to defaults button
- Visual feedback when weights change

### 3. School Detail View
**Comprehensive information panel:**

**Tabs:**
1. **Overview**
   - Hero section with school name, score badge, photo
   - Key facts (address, type, enrollment, religious affiliation)
   - AI-generated summary
   - Quick stats (distance, bike time, exam scores)

2. **Academic**
   - Special programs list
   - Extracurricular activities
   - Exam scores (if available)
   - Student-teacher ratio

3. **Practical**
   - Location map with commute routes
   - Public transport info
   - Open days schedule
   - Contact information
   - Website link

4. **Environment**
   - School culture and values
   - Safety measures
   - Support services
   - Facilities description

5. **Scores Breakdown**
   - Radial chart showing all criterion scores
   - Explanation for each score
   - Comparison to average
   - Strengths and considerations (from AI analysis)

### 4. Comparison View
**Side-by-side comparison of 2-4 schools:**

```
┌──────────────┬──────────────┬──────────────┐
│  School A    │  School B    │  School C    │
├──────────────┼──────────────┼──────────────┤
│  Total: 85   │  Total: 82   │  Total: 79   │
│  🟢          │  🟢          │  🟡          │
├──────────────┼──────────────┼──────────────┤
│ Academic: 90 │ Academic: 85 │ Academic: 75 │
│ Location: 80 │ Location: 90 │ Location: 95 │
│ ...          │ ...          │ ...          │
└──────────────┴──────────────┴──────────────┘
```

**Features:**
- Add schools to comparison (max 4)
- Highlight best value in each row (green)
- Highlight worst value in each row (red/orange)
- Quick comparison charts
- Export comparison as PDF/image

### 5. Map View
**Interactive map showing:**
- All schools as markers
- Color-coded by score (green/yellow/red)
- Home address marker
- Click marker to see school info popup
- Bike routes from home to selected school(s)
- Distance circles (5km, 10km, 15km from home)
- Filter controls (same as table view)
- Cluster markers when zoomed out

**Map Controls:**
- Toggle route display
- Toggle distance circles
- Filter by score range
- Show only VWO-only schools
- Center on home/selected school

### 6. Dashboard/Summary View
**Overview page showing:**
- Total schools analyzed: 45
- Top 5 schools (cards with key info)
- Statistics:
  - Schools by city (pie chart)
  - Schools by type (bar chart)
  - Distance distribution (histogram)
  - Score distribution (histogram)
- Quick insights:
  - Closest VWO-only school
  - Highest-scoring school overall
  - Best school within 5km
  - Schools with gymnasium

## User Flow

### Initial Load:
1. Show dashboard with summary
2. Display top 10 schools in table
3. Show weight adjustment panel (collapsed)

### Exploring Schools:
1. User adjusts filters → table updates
2. User sorts by column → table reorders
3. User clicks school → detail view opens
4. User clicks "Compare" → adds to comparison basket

### Adjusting Weights:
1. User opens weight panel
2. User drags slider → scores recalculate
3. Table rankings update in real-time
4. User sees new top schools

### Comparing Schools:
1. User selects 2-4 schools
2. Comparison view opens
3. Side-by-side details shown
4. Charts visualize differences

### Map Exploration:
1. User switches to map view
2. Schools plotted with home marker
3. User clicks school → popup with basic info
4. User clicks "Show Route" → bike route drawn

## Technical Architecture

### File Structure:
```
frontend/
├── public/
│   └── data/
│       └── schools-scored.json
├── src/
│   ├── components/
│   │   ├── SchoolTable.tsx
│   │   ├── WeightPanel.tsx
│   │   ├── SchoolDetail.tsx
│   │   ├── ComparisonView.tsx
│   │   ├── MapView.tsx
│   │   └── Dashboard.tsx
│   ├── hooks/
│   │   ├── useSchools.ts
│   │   ├── useScoring.ts
│   │   └── useFilters.ts
│   ├── lib/
│   │   ├── scoring.ts
│   │   ├── filtering.ts
│   │   └── utils.ts
│   ├── types/
│   │   └── school.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
└── vite.config.ts
```

### State Management:

```typescript
interface AppState {
  schools: School[]
  weights: Weights
  filters: Filters
  selectedSchools: string[]  // IDs for comparison
  sortConfig: SortConfig
  viewMode: 'table' | 'map' | 'comparison' | 'dashboard'
}
```

### Scoring in Frontend:

```typescript
// Re-implement scoring engine in TypeScript
function calculateScore(school: School, weights: Weights): ScoredSchool {
  // Same logic as Python scoring engine
  // Allows real-time recalculation
}

function rankSchools(schools: School[], weights: Weights): ScoredSchool[] {
  return schools
    .map(school => calculateScore(school, weights))
    .sort((a, b) => b.totalScore - a.totalScore)
    .map((school, index) => ({ ...school, rank: index + 1 }))
}
```

### Performance Optimizations:
- Memoize score calculations with useMemo
- Virtualize long tables (react-virtual)
- Debounce weight slider updates
- Lazy load detail views
- Progressive loading for map markers

## UI/UX Design Principles

### Visual Design:
- Clean, modern interface
- High contrast for readability
- Color-blind friendly palette
- Responsive (mobile, tablet, desktop)
- Dark mode support

### Accessibility:
- Keyboard navigation
- Screen reader support
- ARIA labels
- Focus indicators
- Semantic HTML

### User Experience:
- Fast, instant feedback
- Clear visual hierarchy
- Progressive disclosure (don't overwhelm)
- Helpful empty states
- Loading indicators
- Error handling with friendly messages

## Key Interactions

### Weight Adjustment:
```
User drags slider
  ↓
Update weight state
  ↓
Recalculate all scores (memoized)
  ↓
Update rankings
  ↓
Re-render table (virtual)
  ↓
Smooth transition (< 100ms)
```

### Filtering:
```
User changes filter
  ↓
Update filter state
  ↓
Filter schools array
  ↓
Re-rank filtered schools
  ↓
Update table
```

## Development Phases

### Phase 1: Setup & Core UI (Week 1)
- Initialize project (Vite + React + TypeScript)
- Set up Tailwind CSS
- Create basic layout and routing
- Implement school data loading
- Build basic table view

### Phase 2: Scoring Integration (Week 2)
- Port scoring engine to TypeScript
- Implement weight adjustment panel
- Connect weights to table
- Test real-time recalculation
- Add score breakdowns

### Phase 3: Detail & Comparison Views (Week 3)
- Build school detail view
- Implement comparison view
- Add charts (Recharts)
- Create AI analysis display
- Polish interactions

### Phase 4: Map Integration (Week 4)
- Integrate Leaflet
- Plot schools on map
- Add home marker
- Draw bike routes
- Implement map filters

### Phase 5: Dashboard & Polish (Week 5)
- Create dashboard view
- Add statistics and insights
- Implement export features
- Performance optimization
- Accessibility audit
- User testing

### Phase 6: Deployment (Week 6)
- Build production bundle
- Deploy to Vercel/Netlify
- Set up domain (optional)
- Analytics setup
- Documentation

## Export Features

### PDF Export:
- School comparison report
- Top 10 schools with details
- Customized with selected weights

### CSV Export:
- All schools with scores
- Filtered schools
- Comparison data

### Share Feature:
- Generate shareable URL with:
  - Selected weights
  - Active filters
  - Selected schools
- URL encoded state

## Mobile Responsiveness

### Breakpoints:
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### Mobile Adaptations:
- Stack table columns vertically
- Collapsible filters
- Simplified weight panel
- Touch-friendly controls
- Bottom sheet for details

## Success Metrics

### Performance:
- Initial load: < 2s
- Weight adjustment response: < 100ms
- Table sort/filter: < 200ms
- Lighthouse score: > 90

### Usability:
- Can find top school in < 30s
- Can adjust weights intuitively
- Can compare schools easily
- Works on mobile

## Future Enhancements (Post-MVP)

1. **User Accounts**
   - Save custom weight profiles
   - Bookmark favorite schools
   - Share profiles with family

2. **Advanced Filters**
   - Multiple criteria AND/OR logic
   - Saved filter presets
   - "Schools like this" recommendation

3. **Social Features**
   - Parent reviews/comments
   - Questions & answers
   - School ambassador contact

4. **Data Updates**
   - Admin panel for data updates
   - Automatic data refresh
   - Change history

5. **AI Enhancements**
   - Chat interface: "Find me a school that..."
   - Personalized recommendations
   - Natural language queries

## Deliverables

1. **Complete web application** (deployed and accessible)
2. **Source code** (GitHub repository)
3. **User guide** (README + in-app help)
4. **Demo video** (walkthrough of features)
5. **Technical documentation** (architecture, API docs)

## Testing Plan

### Unit Tests:
- Scoring functions
- Filtering logic
- Utility functions

### Integration Tests:
- Weight adjustment → score update
- Filter → table update
- Comparison selection

### E2E Tests (Playwright/Cypress):
- Load app → see schools
- Adjust weights → rankings change
- Select schools → compare view
- Export comparison

### User Testing:
- 3-5 parent testers
- Task-based scenarios
- Feedback survey
- Iterate based on feedback

## Timeline Estimate

- **Planning & Design**: 1 week
- **Development**: 5-6 weeks
- **Testing & Refinement**: 1 week
- **Deployment**: 3 days
- **Total**: ~8 weeks

## Budget Considerations

### Free Tier Options:
- Hosting: Vercel/Netlify (free for personal)
- Maps: Leaflet + OpenStreetMap (free)
- Analytics: Google Analytics (free)
- Domain: Optional (~€10/year)

### Paid Options:
- Maps: Google Maps API (~€200/month if heavy usage)
- Hosting: Premium tiers if needed
- CDN: Cloudflare Pro
