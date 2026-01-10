Middelbare School research
--------------------------

I want to build a tool to support the choice of different Middelbare School (secondary school) options for a specific student that is going to transition from primary school to secondary school next year.

The tool should collect and analyze different information about VWO schools in Amsterdam and Amstelveen, and provide 
(1) A table containing the full list of schools with their characteristics, rich information and AI analysis.
(2) Scores for each school based on different criteria.
(3) An interactive tool to allow providing different weights to the criteria and see how the scores change.

To build this tool, we would need to gather data on the following schools from various sources. 
Here are some websites which might be useful for gathering data, but I assume that there would be other sources that would be required as well:
- https://schoolkeuze020.nl/
- https://schoolwijzer.amsterdam.nl/nl/vo
- https://onderwijsconsument.nl/
- https://www.oudersteunpunt.nl/

These are some examples for websites that contain information about schools in Amsterdam. You would need to explore these websites and possibly others (for Amstelveen, e.g.) to gather comprehensive data on the schools.

These are the main groups of characteristics that we would want to gather for each school:
1. Basic Information:
    - Name of the school
    - Address
    - Contact information (phone number, email, website)
    - Type of school (e.g., VMBO, HAVO, VWO, etc.)
    - Religious affiliation (if any)    
    - Number of students enrolled (per program)
    - Hours of operation (school days, school hours)
2. Academic Performance:
    - Average exam scores
    - Graduation rates
    - Student-teacher ratio
    - Special programs offered (e.g., gifted education, vocational training)
    - Extracurricular activities offered
3. Facilities:
    - Quality of classrooms and laboratories
    - Sports facilities
    - Library resources
    - Technology availability (computers, internet access)
4. Student Support:
    - Counseling services
    - Newcomers class/Language support for non-native speakers
    - Special education programs
    - Language support for non-native speakers
    - After-school programs
5. School Environment:
    - Safety measures
    - Student diversity
    - Parent and community involvement
    - School culture and values
6. Location and Accessibility:
    - Proximity to public transportation
    - Accessibility for students with disabilities
    - Commute times from the student's home (Judith Leijsterweg 30, Amstelveen) - both by public transport and by bike, including number of transfers for public transport.
7. Reviews and Reputation:
    - Parent and student reviews
    - Awards and recognitions
    - Alumni success stories
8. Practical Information:
    - Dates for open days and information sessions
    - Website links for more information

Part 1: Collect, analyze and enrich the data into a JSON file
Part 2: Devise a scoring system based on the criteria above
Part 3: Build an interactive tool to visualize the scores based on user-defined weights