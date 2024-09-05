import streamlit as st


def style_background_team_fdr(cell_value):
    """Used to apply background highlighting to the teams FDR matrix"""

    bg = "background-color:"
    team_str = 0

    if cell_value != "":
        team_str = int(cell_value[-1])

    if team_str == 1:
        return f"{bg} darkgreen;"
    elif team_str == 2:
        return f"{bg} #09fc7b;"
    elif team_str == 3:
        return f"{bg} #e7e7e8;"
    elif team_str == 4:
        return f"{bg} #ff1651; color: #ffffff;"
    elif team_str == 5:
        return f"{bg} #80072d; color: #ffffff;"
    else:
        return ""


def style_background_player_fdr(cell_value):
    """Used to apply background highlighting to the player FDR matrix"""

    bg = "background-color:"

    if cell_value == 1:
        return f"{bg} darkgreen;"
    elif cell_value == 2:
        return f"{bg} #09fc7b;"
    elif cell_value == 3:
        return f"{bg} #e7e7e8;"
    elif cell_value == 4:
        return f"{bg} #ff1651; color: #ffffff;"
    elif cell_value == 5:
        return f"{bg} #80072d; color: #ffffff;"
    else:
        return ""


style_players = {
    "pos": st.column_config.TextColumn("Pos", help="Position"),
    "player_name": st.column_config.TextColumn("Player"),
    "team": st.column_config.TextColumn("Team"),
    "£": st.column_config.NumberColumn("£", help="Current price"),
    "ST": st.column_config.NumberColumn("ST", help="Games started"),
    "MP": st.column_config.NumberColumn("MP", help="Minutes played"),
    "Pts": st.column_config.NumberColumn("Pts", help="Points scored"),
    "GS": st.column_config.NumberColumn("GS", help="Goals"),
    "A": st.column_config.NumberColumn("A", help="Assists"),
    "GI": st.column_config.NumberColumn("GI", help="Goal involvements (G + A)"),
    "xG": st.column_config.NumberColumn("xG", help="Expected goals"),
    "xA": st.column_config.NumberColumn("xA", help="Expected assists"),
    "xGI": st.column_config.NumberColumn("xGI", help="Expected goal involvements"),
    "PPG": st.column_config.NumberColumn("PPG", help="Points per game"),
    "Pts90": st.column_config.NumberColumn("P90", help="Points / 90 minutes"),
    "GS90": st.column_config.NumberColumn("GS90", help="Goals / 90 minutes"),
    "A90": st.column_config.NumberColumn("A90", help="Assists / 90 minutes"),
    "GI90": st.column_config.NumberColumn("GI90", help="(G + A) / 90 minutes"),
    "xG90": st.column_config.NumberColumn("xG90", help="Expected goals / 90 minutes"),
    "xA90": st.column_config.NumberColumn("xA90", help="Expected assists / 90 minutes"),
    "xGI90": st.column_config.NumberColumn("xGI90", help="(xG + xA) / 90 minutes"),
    "CS": st.column_config.NumberColumn("CS", help="Clean sheets"),
    "GC": st.column_config.NumberColumn("GC", help="Goals conceded"),
    "xGC": st.column_config.NumberColumn("xGC", help="Expected goals conceded"),
    "GC90": st.column_config.NumberColumn("GC90", help="Goals conceded / 90 minutes"),
    "xGC90": st.column_config.NumberColumn("xGC90", help="xG conceded / 90 minutes"),
    "B": st.column_config.NumberColumn("B", help="Bonus points"),
    "BPS90": st.column_config.NumberColumn("BPS90", help="BPS / 90 minutes"),
    "I": st.column_config.NumberColumn("I", help="Influence"),
    "C": st.column_config.NumberColumn("C", help="Creativity"),
    "T": st.column_config.NumberColumn("T", help="Threat"),
    "II": st.column_config.NumberColumn("II", help="ICT index"),
    "I90": st.column_config.NumberColumn("I90", help="Influence / 90 minutes"),
    "C90": st.column_config.NumberColumn("C90", help="Creativity / 90 minutes"),
    "T90": st.column_config.NumberColumn("T90", help="Threat / 90 minutes"),
    "II90": st.column_config.NumberColumn("II90", help="ICT index / 90 minutes"),
    "TSB%": st.column_config.NumberColumn("TSB%", help="Teams selected by %"),
}
