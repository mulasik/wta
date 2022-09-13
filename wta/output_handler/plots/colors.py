from matplotlib import colors as pltc


class Colors:

    SEN_COLORS = {
        'unchanged': 'mistyrose',
        'new': 'darkslategrey',
        'deleted': 'seashell',
        'modified through deletion': 'lightcoral',
        'modified through insertion': 'cadetblue',
        'modified through append': 'teal'
    }
    TS_COLORS = {
        'deletion': 'lightcoral',
        'insertion': 'cadetblue',
        'append': 'teal',
        '': 'w'
    }
    POS_COLORS = {
        'NOUN': 'lightcoral',
        'DET': 'darkred',
        'ADP': 'orange',
        'ADV': 'darkgreen',
        'PRON': 'darkcyan',
        'VERB': 'skyblue',
        'PART': 'slateblue',
        'AUX': 'indigo',
        'ADJ': 'purple',
        'PROPN': 'mediumvioletred',
        'CCONJ': 'lightblue',
        'SCONJ': 'pink',
        'NUM': 'gold',
        'OTHER': 'silver'
    }
    AVAILABLE_COLORS = [k for k, v in pltc.cnames.items() if k not in [
        'white', 'snow', 'whitesmoke', 'seashell', 'antiquewhite', 'oldlace', 'floralwhite', 'cornsilk', 'ivory',
        'honeydew', 'aliceblue', 'mintcream', 'azure', 'ghostwhite', 'lavenderblush', 'beige', 'bisque', 'black'
    ]]

    @classmethod
    def assign_colors_to_sens(cls, senhis):
        """
        Assigns colors to sentences in sentence history.
        Each sentence has a unique color.
        Returns:
            The mapping of colors to sentences.
        """
        sen_colors = {}
        for id, sen_id in enumerate(list(senhis.keys())):
            sen_colors.update({sen_id: cls.AVAILABLE_COLORS[id]})
        return sen_colors

    @classmethod
    def assign_color_to_pos(cls, pos_list):
        colors = []
        for pos in pos_list:
            if pos in Colors.POS_COLORS:
                colors.append(cls.POS_COLORS[pos])
            else:
                colors.append(cls.POS_COLORS['OTHER'])
        return colors

    @classmethod
    def assign_color_to_number_versions(cls, number_versions):
        colors = []
        for nv in number_versions:
            if nv == 1:
                colors.append('grey')
            if 1 < nv <= 10:
                colors.append('pink')
            if 10 < nv <= 15:
                colors.append('indianred')
            if 15 < nv <= 20:
                colors.append('firebrick')
            if nv > 20:
                colors.append('darkred')
        return colors
