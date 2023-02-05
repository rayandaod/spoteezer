def extract_info_simple(self, artists_key=None, item_name_key=None):
        """Extracts basic information about the item.

        Args:
            artists_key (str, optional): Key to get the artists. Defaults to None.
            item_name_key (str, optional): Key to get the item name. Defaults to None.

        Returns:
            dict: Basic information extracted, e.g track name, album name, artist name.
        """

        # Initialize the info dictionary
        info_simple = {}

        # Get the artist or artists
        def _get_artists(info_simple, raw_info, artists_key):

            # Special case for Deezer (not perfect implementation for now lmao)
            if type(self) == DeezerItem and artists_key not in raw_info:
                artists_key = 'artist'

            if type(raw_info[artists_key]) == list and len(raw_info[artists_key]) > 1:
                info_simple['artists'] = ', '.join(
                    [raw_info[artists_key][i]['name'] for i in range(len(raw_info[artists_key]))])
            else:
                info_simple['artist'] = raw_info[artists_key][0]['name'] if type(
                    raw_info[artists_key]) == list else raw_info[artists_key]['name']
            return info_simple

        if self.type in ['track', 'album']:
            info_simple[self.type] = self.raw_info[item_name_key]
            info_simple = _get_artists(info_simple, self.raw_info, artists_key)

            if self.type == 'track':
                info_simple['album'] = self.raw_info['album'][item_name_key]

        elif self.type == 'artist':
            if type(self) == DeezerItem:
                info_simple['artist'] = self.raw_info['name']
            else:
                info_simple['artist'] = self.raw_info['name']

        return info_simple