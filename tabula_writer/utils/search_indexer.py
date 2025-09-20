import re
import os

class SearchIndexer:
    def __init__(self):
        self.index = {'wikilinks': {}, 'tags': {}}
        self.all_paths = set()

    def build_index(self, files_info):
        """Builds the entire index from a list of all project files."""
        # Reset the index completely on a full rebuild
        self.index = {'wikilinks': {}, 'tags': {}}
        self.all_paths.clear()

        wikilink_pattern = re.compile(r'\[\[(.*?)\]\]')
        tag_pattern = re.compile(r'(@\w+)')

        for file_info in files_info:
            path = file_info['path']
            self.all_paths.add(path)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                found_wikilinks = set(wikilink_pattern.findall(content))
                for link in found_wikilinks:
                    link_key = link.lower()
                    if link_key not in self.index['wikilinks']:
                        self.index['wikilinks'][link_key] = set()
                    self.index['wikilinks'][link_key].add(path)

                found_tags = set(tag_pattern.findall(content))
                for tag in found_tags:
                    tag_key = tag.lower()
                    if tag_key not in self.index['tags']:
                        self.index['tags'][tag_key] = set()
                    self.index['tags'][tag_key].add(path)
            except (IOError, UnicodeDecodeError):
                continue

    def _clear_file_from_index(self, path):
        """Removes all references to a given file path from the index."""
        self.all_paths.discard(path)
        for link_key, paths in self.index['wikilinks'].items():
            paths.discard(path)
        for tag_key, paths in self.index['tags'].items():
            paths.discard(path)

    def update_file(self, path, content):
        """Updates the index for a single file given its path and content."""
        self._clear_file_from_index(path)
        self.all_paths.add(path)
        
        wikilink_pattern = re.compile(r'\[\[(.*?)\]\]')
        tag_pattern = re.compile(r'(@\w+)')

        found_wikilinks = set(wikilink_pattern.findall(content))
        for link in found_wikilinks:
            link_key = link.lower()
            if link_key not in self.index['wikilinks']:
                self.index['wikilinks'][link_key] = set()
            self.index['wikilinks'][link_key].add(path)

        found_tags = set(tag_pattern.findall(content))
        for tag in found_tags:
            tag_key = tag.lower()
            if tag_key not in self.index['tags']:
                self.index['tags'][tag_key] = set()
            self.index['tags'][tag_key].add(path)

    def get_occurrences_for_wikilink(self, link_text):
        """Gets all file paths containing a given wikilink."""
        return list(self.index['wikilinks'].get(link_text.lower(), []))

    def get_files_for_tag(self, tag_text):
        """Gets all file paths containing a given tag."""
        return list(self.index['tags'].get(tag_text.lower(), []))

    def get_all_indexed_paths(self):
        """Returns a list of all file paths currently in the index."""
        return list(self.all_paths)
