"""
School Selection Tool - Interactive UI

Streamlit application for browsing, comparing, and ranking schools.
"""

import streamlit as st
import json
from pathlib import Path
from scoring import SchoolScorer
import pandas as pd
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz

# Page config
st.set_page_config(
    page_title="Amsterdam School Selector",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .school-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
    }
    .score-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
        font-size: 0.9em;
    }
    .score-excellent { background-color: #10b981; color: white; }
    .score-good { background-color: #3b82f6; color: white; }
    .score-fair { background-color: #f59e0b; color: white; }
    .score-poor { background-color: #ef4444; color: white; }
    .metric-label {
        font-size: 0.85em;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# Initialize scorer
@st.cache_resource
def get_scorer():
    return SchoolScorer()

scorer = get_scorer()

# Favorites persistence
FAVORITES_FILE = Path('data/favorites.json')

def load_favorites():
    """Load favorites from file."""
    if FAVORITES_FILE.exists():
        try:
            with open(FAVORITES_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get('favorites', []))
        except (json.JSONDecodeError, IOError):
            return set()
    return set()

def save_favorites(favorites):
    """Save favorites to file."""
    try:
        FAVORITES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(FAVORITES_FILE, 'w') as f:
            json.dump({'favorites': list(favorites)}, f, indent=2)
    except IOError as e:
        st.error(f"Could not save favorites: {e}")

def parse_time_range(time_str):
    """Parse time range string like '14:30-16:30' into start and end times."""
    try:
        if '-' in time_str:
            start_str, end_str = time_str.split('-')
            start_hour, start_min = map(int, start_str.strip().split(':'))
            end_hour, end_min = map(int, end_str.strip().split(':'))
            return (start_hour, start_min), (end_hour, end_min)
    except:
        # Default to 2-hour window starting at 10:00
        return (10, 0), (12, 0)
    return (10, 0), (12, 0)

def generate_ics_file(schools):
    """Generate ICS calendar file for all open days from given schools."""
    cal = Calendar()
    cal.add('prodid', '-//School Selection Tool//Open Days//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'School Open Days')
    cal.add('x-wr-caldesc', 'Open days for favorite schools in Amsterdam/Amstelveen')

    amsterdam_tz = pytz.timezone('Europe/Amsterdam')

    for school in schools:
        school_name = school['basic_info']['name']
        school_address = school['basic_info'].get('address', '')
        school_city = school['basic_info'].get('city', '')
        open_days = school.get('practical_info', {}).get('open_days', [])

        for open_day in open_days:
            event = Event()

            # Parse date
            date_str = open_day.get('date')
            if not date_str:
                continue

            event_date = datetime.strptime(date_str, '%Y-%m-%d')

            # Parse time
            time_str = open_day.get('time', '')
            (start_h, start_m), (end_h, end_m) = parse_time_range(time_str)

            # Create datetime objects with timezone
            start_dt = amsterdam_tz.localize(
                datetime(event_date.year, event_date.month, event_date.day, start_h, start_m)
            )
            end_dt = amsterdam_tz.localize(
                datetime(event_date.year, event_date.month, event_date.day, end_h, end_m)
            )

            # Event details
            event_type = open_day.get('type', 'Open Day')
            reg_required = open_day.get('registration_required', False)

            summary = f"{school_name} - {event_type}"
            description = f"School: {school_name}\n"
            description += f"Event Type: {event_type}\n"
            if reg_required:
                description += "⚠️ Registration required\n"
            description += f"\nAddress: {school_address}, {school_city}"

            # Add school website if available
            website = school['basic_info'].get('contact', {}).get('website')
            if website:
                description += f"\nWebsite: {website}"

            event.add('summary', summary)
            event.add('description', description)
            event.add('dtstart', start_dt)
            event.add('dtend', end_dt)
            event.add('location', f"{school_address}, {school_city}")
            event.add('dtstamp', datetime.now(amsterdam_tz))

            # Add unique ID
            time_part = (time_str or '').replace(':', '') or 'no-time'
            uid = f"{date_str}-{school['id']}-{time_part}@school-selector"
            event.add('uid', uid)

            cal.add_component(event)

    return cal.to_ical()

# Initialize session state
if 'favorites' not in st.session_state:
    st.session_state.favorites = load_favorites()
if 'weights' not in st.session_state:
    st.session_state.weights = SchoolScorer.DEFAULT_WEIGHTS.copy()
if 'preferences' not in st.session_state:
    st.session_state.preferences = {'school_size': 'medium'}


def get_score_badge_html(score):
    """Generate HTML for score badge."""
    if score is None:
        return '<span class="score-badge" style="background-color: #9ca3af;">N/A</span>'
    elif score >= 85:
        return f'<span class="score-badge score-excellent">{score:.1f}</span>'
    elif score >= 70:
        return f'<span class="score-badge score-good">{score:.1f}</span>'
    elif score >= 50:
        return f'<span class="score-badge score-fair">{score:.1f}</span>'
    else:
        return f'<span class="score-badge score-poor">{score:.1f}</span>'


def render_school_card(school, score_data, rank=None):
    """Render a school card with key information."""
    name = school['basic_info']['name']
    school_id = school['id']

    # Favorite button
    is_favorite = school_id in st.session_state.favorites
    fav_label = "★" if is_favorite else "☆"

    col1, col2 = st.columns([0.95, 0.05])

    with col1:
        if rank:
            st.markdown(f"### {rank}. {name}")
        else:
            st.markdown(f"### {name}")

    with col2:
        if st.button(fav_label, key=f"fav_{school_id}", help="Add to favorites"):
            if is_favorite:
                st.session_state.favorites.remove(school_id)
            else:
                st.session_state.favorites.add(school_id)
            save_favorites(st.session_state.favorites)
            st.rerun()

    # Basic info
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"**Overall Score**")
        composite = score_data['composite_score']
        st.markdown(get_score_badge_html(composite), unsafe_allow_html=True)

    with col2:
        types = ', '.join(school['basic_info'].get('type', []))
        st.markdown(f"**Type**")
        st.write(types)

    with col3:
        city = school['basic_info'].get('city', 'N/A')
        st.markdown(f"**City**")
        st.write(city)

    with col4:
        enrollment = school['basic_info'].get('enrollment', {}).get('total')
        st.markdown(f"**Students**")
        st.write(f"{enrollment}" if enrollment else "N/A")

    # Category scores
    st.markdown("#### Scores by Category")
    cols = st.columns(4)

    categories = [
        ('academic_performance', 'Academic', '📚'),
        ('proximity', 'Proximity', '🚴'),
        ('parent_satisfaction', 'Parents', '👨‍👩‍👧'),
        ('student_satisfaction', 'Students', '🎓'),
        ('facilities', 'Facilities', '🏫'),
        ('extracurriculars', 'Activities', '⚽'),
        ('special_programs', 'Programs', '✨'),
        ('school_size', 'Size Fit', '📊')
    ]

    for idx, (key, label, icon) in enumerate(categories):
        with cols[idx % 4]:
            score_info = score_data['category_scores'].get(key, {})
            score = score_info.get('score')
            details = score_info.get('details', '')

            st.markdown(f"{icon} **{label}**")
            if score is not None:
                st.markdown(get_score_badge_html(score), unsafe_allow_html=True)
                st.caption(details)
            else:
                st.markdown(get_score_badge_html(None), unsafe_allow_html=True)
                st.caption(details)

    # Expandable details
    with st.expander("View Full Details"):
        render_school_details(school)

    st.markdown("---")


def render_school_details(school):
    """Render full school details."""
    # Contact & Location
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Contact Information**")
        contact = school['basic_info'].get('contact', {})
        st.write(f"📞 {contact.get('phone', 'N/A')}")
        st.write(f"📧 {contact.get('email', 'N/A')}")
        if contact.get('website'):
            st.write(f"🌐 [{contact['website']}]({contact['website']})")

        # onderwijsconsument.nl link
        links = school.get('practical_info', {}).get('links', [])
        oc_links = [link for link in links if 'onderwijsconsument.nl/scholenoverzicht' in str(link)]
        if oc_links:
            st.write(f"📊 [School Profile (onderwijsconsument.nl)]({oc_links[0]})")

        st.markdown("**Address**")
        address = school['basic_info'].get('address', 'N/A')
        postal = school['basic_info'].get('postal_code', '')
        city = school['basic_info'].get('city', '')
        st.write(f"{address}, {postal} {city}")

    with col2:
        st.markdown("**Commute Information**")

        bike = school.get('location', {}).get('bike_accessibility', {})
        if bike.get('duration_minutes'):
            st.write(f"🚴 Bike: {bike['duration_text']} ({bike['distance_text']})")

        transit = school.get('location', {}).get('public_transport', {}).get('commute_from_home', {})
        if transit.get('duration_minutes'):
            st.write(f"🚌 Transit: {transit['duration_text']} ({transit.get('transfers', 0)} transfers)")

        st.markdown("**Religious Affiliation**")
        affiliation = school['basic_info'].get('religious_affiliation', 'N/A')
        st.write(affiliation)

    # Map
    coordinates = school.get('location', {}).get('coordinates', {})
    if coordinates.get('lat') and coordinates.get('lon'):
        st.markdown("**Location Map**")
        map_data = pd.DataFrame({
            'lat': [coordinates['lat']],
            'lon': [coordinates['lon']]
        })
        st.map(map_data, zoom=14)

    # Academic Performance
    st.markdown("**Academic Performance**")
    exam_scores = school.get('academic_performance', {}).get('exam_scores', {})

    if exam_scores:
        for level in ['vmbo', 'havo', 'vwo']:
            if level in exam_scores:
                data = exam_scores[level]
                rate = data.get('pass_rate_2024_2025')
                avg_5yr = data.get('average_pass_rate_5yr')
                candidates = data.get('candidates_2024_2025')

                if rate:
                    st.write(f"  - **{level.upper()}**: {rate}% pass rate ({candidates} candidates), 5-yr avg: {avg_5yr}%")
    else:
        st.write("No exam data available")

    # Special Programs
    programs = school.get('academic_performance', {}).get('special_programs', [])
    if programs:
        st.markdown("**Special Programs**")
        for program in programs:
            st.write(f"  - {program}")

    # Extracurricular Activities
    activities = school.get('academic_performance', {}).get('extracurricular_activities', [])
    if activities:
        st.markdown("**Extracurricular Activities**")
        st.write(", ".join(activities))

    # Facilities
    facilities = school.get('facilities', {})
    if facilities.get('classrooms_labs_quality'):
        st.markdown("**Facilities**")
        st.write(facilities['classrooms_labs_quality'])

    # Student Support
    support = school.get('student_support', {})
    if support.get('special_education'):
        st.markdown("**Special Education Support**")
        for item in support['special_education']:
            st.write(f"  - {item}")

    # Open Days
    open_days = school.get('practical_info', {}).get('open_days', [])
    if open_days:
        st.markdown("**Upcoming Open Days (2026)**")
        for event in open_days[:5]:  # Show first 5
            date = event.get('date', '')
            time = event.get('time', '')
            event_type = event.get('type', '')
            st.write(f"  - {date} {time} - {event_type}")

    # AI Analysis
    ai_analysis = school.get('ai_analysis', {})
    if ai_analysis:
        st.markdown("**AI Analysis**")

        if ai_analysis.get('summary'):
            st.info(ai_analysis['summary'])

        if ai_analysis.get('strengths'):
            st.markdown("*Strengths:*")
            for strength in ai_analysis['strengths'][:5]:
                st.write(f"  ✓ {strength}")

        if ai_analysis.get('best_fit_for'):
            st.markdown("*Best fit for:*")
            for fit in ai_analysis['best_fit_for'][:3]:
                st.write(f"  • {fit}")


# Sidebar
with st.sidebar:
    st.title("🎓 School Selector")

    page = st.radio("Navigation", [
        "🏠 Home",
        "📊 Rankings",
        "⚖️ Compare Schools",
        "⭐ Favorites",
        "📅 Open Days Calendar",
        "⚙️ Customize Weights"
    ])

    st.markdown("---")
    st.markdown(f"**Total Schools:** {len(scorer.schools)}")
    st.markdown(f"**Favorites:** {len(st.session_state.favorites)}")


# Main content
if page == "🏠 Home":
    st.title("Amsterdam/Amstelveen School Selection Tool")

    st.markdown("""
    Welcome to the school selection tool! This application helps you find the best secondary school
    (middelbare school) based on comprehensive data and your personal preferences.

    ### Features:
    - **📊 Rankings**: View schools ranked by overall score with customizable criteria
    - **⚖️ Compare**: Side-by-side comparison of schools
    - **⭐ Favorites**: Save and manage your shortlist
    - **📅 Open Days Calendar**: View all open days and download ICS file for Google Calendar
    - **⚙️ Customize**: Adjust weights for different criteria

    ### Scoring Criteria:
    - **Academic Performance** (30%): Exam pass rates and trends
    - **Proximity** (20%): Bike and transit commute times
    - **Parent Satisfaction** (15%): Parent ratings and recommendations
    - **Student Satisfaction** (10%): Student feedback
    - **Facilities** (10%): Technology, sports, specialized rooms
    - **School Size** (5%): Enrollment size preference match
    - **Extracurriculars** (5%): Activities and programs
    - **Special Programs** (5%): Unique educational offerings

    Use the sidebar to navigate between different views.
    """)

    # Quick stats
    st.markdown("### Quick Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        schools_with_exam = sum(1 for s in scorer.schools
                               if s.get('academic_performance', {}).get('exam_scores'))
        st.metric("Schools with Exam Data", schools_with_exam)

    with col2:
        schools_with_ratings = sum(1 for s in scorer.schools
                                  if s.get('reviews_reputation', {}).get('parent_reviews'))
        st.metric("Schools with Parent Ratings", schools_with_ratings)

    with col3:
        avg_commute = sum(s.get('location', {}).get('bike_accessibility', {}).get('duration_minutes', 0)
                         for s in scorer.schools if s.get('location', {}).get('bike_accessibility', {}).get('duration_minutes')) / len(scorer.schools)
        st.metric("Avg Bike Commute", f"{avg_commute:.1f} mins")

    with col4:
        total_enrollment = sum(s.get('basic_info', {}).get('enrollment', {}).get('total', 0)
                              for s in scorer.schools if s.get('basic_info', {}).get('enrollment', {}).get('total'))
        st.metric("Total Students", f"{total_enrollment:,}")


elif page == "📊 Rankings":
    st.title("School Rankings")

    # Filters
    with st.expander("🔍 Filters", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            filter_city = st.selectbox("City", ["All", "Amsterdam", "Amstelveen"])

        with col2:
            filter_type = st.multiselect("School Type", ["VWO", "HAVO", "VMBO", "Gymnasium"])

        with col3:
            max_commute = st.slider("Max Bike Commute (minutes)", 0, 60, 60)

    # Build filter dict
    filters = {}
    if filter_city != "All":
        filters['city'] = filter_city
    if filter_type:
        filters['school_type'] = filter_type
    if max_commute < 60:
        filters['max_commute_minutes'] = max_commute

    # Get rankings
    rankings = scorer.rank_schools(
        weights=st.session_state.weights,
        preferences=st.session_state.preferences,
        filters=filters if filters else None
    )

    st.markdown(f"### Top Schools ({len(rankings)} total)")

    if not rankings:
        st.warning("No schools match your filters.")
    else:
        # Display rankings
        for i, result in enumerate(rankings, 1):
            render_school_card(result['school'], result['score_data'], rank=i)


elif page == "⚖️ Compare Schools":
    st.title("Compare Schools")

    st.markdown("Select 2-4 schools to compare side by side:")

    # School selection
    school_names = {s['basic_info']['name']: s['id'] for s in scorer.schools}
    selected_names = st.multiselect(
        "Select schools to compare",
        options=sorted(school_names.keys()),
        max_selections=4
    )

    if len(selected_names) < 2:
        st.info("Please select at least 2 schools to compare.")
    else:
        selected_schools = [s for s in scorer.schools if s['basic_info']['name'] in selected_names]

        # Calculate scores for selected schools
        school_data = []
        for school in selected_schools:
            score_data = scorer.calculate_composite_score(
                school,
                weights=st.session_state.weights,
                preferences=st.session_state.preferences
            )
            school_data.append((school, score_data))

        # Comparison table
        st.markdown("### Score Comparison")

        comparison_data = {
            'School': [s[0]['basic_info']['name'] for s in school_data],
            'Overall Score': [s[1]['composite_score'] for s in school_data],
        }

        # Add category scores
        categories = [
            'academic_performance',
            'proximity',
            'parent_satisfaction',
            'student_satisfaction',
            'facilities',
            'school_size',
            'extracurriculars',
            'special_programs'
        ]

        for cat in categories:
            comparison_data[cat.replace('_', ' ').title()] = [
                s[1]['category_scores'][cat]['score'] for s in school_data
            ]

        df = pd.DataFrame(comparison_data)

        # Style the dataframe
        def highlight_max(s):
            if s.name == 'School':
                return [''] * len(s)
            is_max = s == s.max()
            return ['background-color: lightgreen' if v else '' for v in is_max]

        styled_df = df.style.apply(highlight_max, axis=0).format({
            col: "{:.1f}" for col in df.columns if col != 'School'
        })

        st.dataframe(styled_df, use_container_width=True)

        # Detailed comparison
        st.markdown("### Detailed Information")

        cols = st.columns(len(selected_schools))

        for idx, (school, score_data) in enumerate(school_data):
            with cols[idx]:
                st.markdown(f"#### {school['basic_info']['name']}")

                # Basic info
                st.write(f"**Type:** {', '.join(school['basic_info'].get('type', []))}")
                enrollment = school['basic_info'].get('enrollment', {}).get('total')
                st.write(f"**Students:** {enrollment if enrollment else 'N/A'}")

                # Commute
                bike = school.get('location', {}).get('bike_accessibility', {})
                if bike.get('duration_minutes'):
                    st.write(f"**Bike:** {bike['duration_text']}")

                # Exam scores
                exam_scores = school.get('academic_performance', {}).get('exam_scores', {})
                if 'vwo' in exam_scores:
                    rate = exam_scores['vwo'].get('pass_rate_2024_2025')
                    st.write(f"**VWO Pass Rate:** {rate}%")

                # Ratings
                parent_reviews = school.get('reviews_reputation', {}).get('parent_reviews', [])
                if parent_reviews:
                    st.write(f"**Parent Rating:** {parent_reviews[0]['overall_rating']:.1f}/10")

                # Link
                website = school['basic_info'].get('contact', {}).get('website')
                if website:
                    st.markdown(f"[🌐 Visit Website]({website})")


elif page == "⭐ Favorites":
    st.title("Your Favorites")

    if not st.session_state.favorites:
        st.info("You haven't added any favorites yet. Use the ☆ button on school cards to add them.")
    else:
        favorite_schools = [s for s in scorer.schools if s['id'] in st.session_state.favorites]

        st.markdown(f"You have **{len(favorite_schools)}** favorite schools:")

        # Get scores for favorites
        results = []
        for school in favorite_schools:
            score_data = scorer.calculate_composite_score(
                school,
                weights=st.session_state.weights,
                preferences=st.session_state.preferences
            )
            results.append({'school': school, 'score_data': score_data})

        # Sort by score
        results.sort(key=lambda x: x['score_data']['composite_score'] or 0, reverse=True)

        for i, result in enumerate(results, 1):
            render_school_card(result['school'], result['score_data'], rank=i)

        # Export option
        if st.button("📄 Export Favorites List"):
            export_data = []
            for result in results:
                school = result['school']
                export_data.append({
                    'Name': school['basic_info']['name'],
                    'Score': result['score_data']['composite_score'],
                    'Type': ', '.join(school['basic_info'].get('type', [])),
                    'City': school['basic_info'].get('city'),
                    'Website': school['basic_info'].get('contact', {}).get('website', '')
                })

            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False)

            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name="favorite_schools.csv",
                mime="text/csv"
            )


elif page == "📅 Open Days Calendar":
    st.title("Open Days Calendar")

    if not st.session_state.favorites:
        st.info("You haven't added any favorites yet. Add some favorites to see their open days!")
    else:
        favorite_schools = [s for s in scorer.schools if s['id'] in st.session_state.favorites]

        # Collect all open days
        all_events = []
        schools_with_events = 0

        for school in favorite_schools:
            school_name = school['basic_info']['name']
            open_days = school.get('practical_info', {}).get('open_days', [])

            if open_days:
                schools_with_events += 1
                for event in open_days:
                    all_events.append({
                        'school': school_name,
                        'school_id': school['id'],
                        'date': event.get('date'),
                        'time': event.get('time'),
                        'type': event.get('type'),
                        'registration_required': event.get('registration_required', False)
                    })

        if not all_events:
            st.warning("None of your favorite schools have open day information available.")
        else:
            st.markdown(f"""
            📊 **{len(all_events)} events** from **{schools_with_events}** schools
            """)

            # Download ICS button
            col1, col2 = st.columns([0.3, 0.7])
            with col1:
                ics_data = generate_ics_file(favorite_schools)
                st.download_button(
                    label="📥 Download Calendar (ICS)",
                    data=ics_data,
                    file_name="school_open_days.ics",
                    mime="text/calendar",
                    help="Download all events to import into Google Calendar, Outlook, or Apple Calendar"
                )

            with col2:
                st.caption("Import this file into your calendar app to add all open days at once")

            st.markdown("---")

            # Sort events by date
            all_events.sort(key=lambda x: x['date'])

            # Group events by month
            from collections import defaultdict
            events_by_month = defaultdict(list)

            for event in all_events:
                date_obj = datetime.strptime(event['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%B %Y')
                events_by_month[month_key].append(event)

            # Display events by month
            for month, events in events_by_month.items():
                st.markdown(f"### {month}")

                for event in events:
                    date_obj = datetime.strptime(event['date'], '%Y-%m-%d')
                    day_name = date_obj.strftime('%A')
                    date_formatted = date_obj.strftime('%d %B')

                    # Color code by school
                    with st.container():
                        col1, col2, col3 = st.columns([0.2, 0.3, 0.5])

                        with col1:
                            st.markdown(f"**{day_name}**")
                            st.markdown(f"{date_formatted}")

                        with col2:
                            st.markdown(f"**{event['school']}**")
                            st.caption(f"🕐 {event['time']}")

                        with col3:
                            st.markdown(f"{event['type']}")
                            if event['registration_required']:
                                st.caption("⚠️ Registration required")

                        st.markdown("---")

            # Summary table
            st.markdown("### Summary by School")

            summary_data = []
            for school in favorite_schools:
                school_name = school['basic_info']['name']
                open_days = school.get('practical_info', {}).get('open_days', [])

                if open_days:
                    dates = [datetime.strptime(od['date'], '%Y-%m-%d').strftime('%d %b')
                             for od in open_days]
                    summary_data.append({
                        'School': school_name,
                        'Events': len(open_days),
                        'Dates': ', '.join(dates)
                    })

            if summary_data:
                df = pd.DataFrame(summary_data)
                st.dataframe(df, use_container_width=True, hide_index=True)


elif page == "⚙️ Customize Weights":
    st.title("Customize Scoring Weights")

    st.markdown("""
    Adjust the weights for each category to match your priorities.
    Weights represent the percentage importance of each criterion.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Academic & Location")

        st.session_state.weights['academic_performance'] = st.slider(
            "📚 Academic Performance",
            0, 50, st.session_state.weights['academic_performance'],
            help="Exam pass rates and historical trends"
        )

        st.session_state.weights['proximity'] = st.slider(
            "🚴 Proximity (Commute Time)",
            0, 40, st.session_state.weights['proximity'],
            help="Bike and transit commute times"
        )

        st.session_state.weights['facilities'] = st.slider(
            "🏫 Facilities",
            0, 20, st.session_state.weights['facilities'],
            help="Technology, sports facilities, specialized rooms"
        )

        st.session_state.weights['school_size'] = st.slider(
            "📊 School Size Match",
            0, 15, st.session_state.weights['school_size'],
            help="How well the school size matches your preference"
        )

    with col2:
        st.markdown("### Satisfaction & Programs")

        st.session_state.weights['parent_satisfaction'] = st.slider(
            "👨‍👩‍👧 Parent Satisfaction",
            0, 30, st.session_state.weights['parent_satisfaction'],
            help="Parent ratings and recommendations"
        )

        st.session_state.weights['student_satisfaction'] = st.slider(
            "🎓 Student Satisfaction",
            0, 25, st.session_state.weights['student_satisfaction'],
            help="Student feedback and ratings"
        )

        st.session_state.weights['extracurriculars'] = st.slider(
            "⚽ Extracurricular Activities",
            0, 15, st.session_state.weights['extracurriculars'],
            help="Sports, arts, and other activities"
        )

        st.session_state.weights['special_programs'] = st.slider(
            "✨ Special Programs",
            0, 15, st.session_state.weights['special_programs'],
            help="Unique educational offerings"
        )

    # Preferences
    st.markdown("### Preferences")

    st.session_state.preferences['school_size'] = st.selectbox(
        "Preferred School Size",
        ["small", "medium", "large", "any"],
        index=["small", "medium", "large", "any"].index(st.session_state.preferences['school_size']),
        help="Small: <500, Medium: 500-1000, Large: 1000-1500, Very Large: >1500"
    )

    # Show total weight
    total_weight = sum(st.session_state.weights.values())
    st.markdown(f"### Total Weight: **{total_weight}%**")

    if total_weight != 100:
        st.warning(f"⚠️ Weights should ideally add up to 100%. Current total: {total_weight}%")

    # Reset button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset to Defaults"):
            st.session_state.weights = SchoolScorer.DEFAULT_WEIGHTS.copy()
            st.session_state.preferences = {'school_size': 'medium'}
            st.rerun()

    with col2:
        st.info("💡 Changes are applied automatically. Use the sidebar to view rankings.")

    # Show current weight distribution
    st.markdown("### Current Weight Distribution")
    weights_df = pd.DataFrame({
        'Category': [k.replace('_', ' ').title() for k in st.session_state.weights.keys()],
        'Weight (%)': list(st.session_state.weights.values())
    })
    st.bar_chart(weights_df.set_index('Category'))


# Footer
st.markdown("---")
st.markdown("*Data last updated: 2026-01-09 | Total schools: {}*".format(len(scorer.schools)))
