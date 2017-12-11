import glob
import ntpath
import sys
import subprocess


class Utils:
    @staticmethod
    def to_string(value):
        if isinstance(value, bytes):
            return value.decode("utf-8")
        if isinstance(value, str):
            return value


class Markdown2:
    @staticmethod
    def _get_command(md_path):
        return [
            "python3",
            "-m",
            "markdown2",
            "--extras",
            "fenced-code-blocks",
            md_path
        ]

    @staticmethod
    def generate(md_path):
        command = Markdown2._get_command(md_path)
        result = subprocess.run(command, stdout=subprocess.PIPE)
        return Utils.to_string(result.stdout)


class Configs:
    def __init__(self):
        self.output_dir = 'build'
        self.input_dir = sys.argv[1]
        self.templates_dir = 'templates'
        self.articles_dir = 'articles'
        self.rss_feed_path = 'rss.xml'

    def templates(self):
        return "{}/{}/".format(self.input_dir, self.templates_dir)

    def output_index(self, index_name):
        return "{}/{}".format(self.output_dir, index_name)

    def articles(self):
        return "{}/{}/".format(self.input_dir, self.articles_dir)


class Templates:
    def __init__(self, configs):
        self.template_extension = '.spybgt'
        self.index_path = self._find_template(configs, 'index.*')
        self.article_path = self._find_template(configs, 'article.*')
        self.article_short_path = self._find_template(configs, 'article_short.*')

    def _find_template(self, configs, pattern):
        found = glob.glob(configs.templates() + pattern + self.template_extension)
        if len(found) == 0:
            raise Exception('No index template found in: ' + configs.templates())

        if len(found) > 1:
            raise Exception('Multiple index templates found: ' + str(found))

        return found[0]

    @staticmethod
    def _load_template(path):
        with open(path, 'r') as file:
            return file.read()

    def output_index_name(self):
        return ntpath.basename(self.index_path).replace('.spybgt', '')

    def load_article_short_template(self):
        return self._load_template(self.article_short_path)


class ArticlesMetadata:
    def __init__(self):
        self.title = ''
        self.date = ''
        self.short = ''

    @staticmethod
    def _extract_raw_metadata(article):
        start_pos = article.find('{')
        end_pos = article.find('}')
        return article[start_pos + 1: end_pos]

    @staticmethod
    def _parse_raw(raw_data):
        parsed = {}
        for line in raw_data.splitlines():
            if len(line.strip()):
                split = line.split(':')
                parsed[split[0].strip()] = split[1].strip()

        return parsed

    def extract_from_article(self, article):
        raw_metadata = self._extract_raw_metadata(article)
        parsed = self._parse_raw(raw_metadata)
        self.title = parsed['title']
        self.date = parsed['date']
        self.short = parsed['short']


class ArticlesGenerator:
    def __init__(self, configs):
        self.configs = configs
        self.templates = Templates(self.configs)

    def _generate_article_list_entry(self, article_path):
        template = self.templates.load_article_short_template()

        with open(article_path, 'r') as file:
            article = file.read()

        metadata = ArticlesMetadata()
        metadata.extract_from_article(article)

        return template.replace('%article.title%', metadata.title) \
            .replace('%article.data%', metadata.date) \
            .replace('%article.short%', metadata.short)

    def generate_articles_list(self):
        articles_paths = glob.glob(self.configs.articles() + '*')
        articles_list = ''

        for article_path in articles_paths:
            articles_list += self._generate_article_list_entry(article_path)

        return articles_list


class Spybg:
    def __init__(self):
        self.configs = Configs()
        self.templates = Templates(self.configs)
        self.articles_generator = ArticlesGenerator(self.configs)

    def generate(self):
        with open(self.templates.index_path, 'r') as file:
            index_template = file.read()

        generated_index = index_template.replace('%SPYBG_ARTICLES_LIST%',
                                                 self.articles_generator.generate_articles_list())

        with open(self.configs.output_index(self.templates.output_index_name()), 'w+') as file:
            file.write(generated_index)


def main():
    #try:
        spybg = Spybg()
        spybg.generate()
    #except Exception as exception:
     #   print(exception)


if __name__ == "__main__":
    main()
