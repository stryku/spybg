import glob
import ntpath
import os
import sys
import markdown2


class Utils:
    @staticmethod
    def to_string(value):
        if isinstance(value, bytes):
            return value.decode("utf-8")
        if isinstance(value, str):
            return value

    @staticmethod
    def create_file_with_dirs(path, mode='w'):
        dir_path = os.path.split(path)[0]
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        return open(path, mode)


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

    def output_article_path(self, art_name):
        return "{}/arts/{}".format(self.output_dir, art_name)

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

    def load_article_template(self):
        return self._load_template(self.article_path)

    def article_extension(self):
        return os.path.splitext(os.path.splitext(self.article_path)[0])[1]


class ArticleInfo:
    def __init__(self, art_path):
        self.title = ''
        self.date = ''
        self.short = ''
        self.content = ''
        self.filename = os.path.splitext(os.path.basename(art_path))[0]

        with open(art_path, 'r') as file:
            article = file.read()
            self.extract_from_article(article)

    @staticmethod
    def get_raw_metadata_pos_info(article):
        return [article.find('{'), article.find('}')]

    @staticmethod
    def _extract_raw_metadata(article):
        pos_info = ArticleInfo.get_raw_metadata_pos_info(article)
        return article[pos_info[0] + 1: pos_info[1]]

    @staticmethod
    def _extract_content(article):
        pos_info = ArticleInfo.get_raw_metadata_pos_info(article)
        return article[pos_info[1] + 1:]

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
        self.content = self._extract_content(article)


class ArticlesGenerator:
    def __init__(self, configs):
        self.configs = configs
        self.templates = Templates(self.configs)

    def _generate_article_list_entry(self, article_path):
        template = self.templates.load_article_short_template()

        art_info = ArticleInfo(article_path)

        return template.replace('%article.title%', art_info.title) \
            .replace('%article.data%', art_info.date) \
            .replace('%article.short%', art_info.short)

    def generate_articles_list(self):
        articles_paths = glob.glob(self.configs.articles() + '*')
        articles_list = ''

        for article_path in articles_paths:
            articles_list += self._generate_article_list_entry(article_path)

        return articles_list

    @staticmethod
    def _remove_article_metadata(article):
        metadata_pos_info = ArticleInfo.get_raw_metadata_pos_info(article)
        return article[metadata_pos_info[1]:]

    def _generate_article(self, article_path):
        template = self.templates.load_article_template()

        art_info = ArticleInfo(article_path)

        article_content = markdown2.markdown(art_info.content, extras=["fenced-code-blocks"])
        generated_article_path = self._get_generated_article_path(article_path)

        generated_article =  template.replace('%article.title%', art_info.title) \
            .replace('%article.date%', art_info.date) \
            .replace('%article.content%', article_content)

        with Utils.create_file_with_dirs(generated_article_path) as file:
            file.write(generated_article)

    def _get_generated_article_path(self, article_path):
        info = ArticleInfo(article_path)
        article_filename = info.filename + self.templates.article_extension()
        return self.configs.output_article_path(article_filename)

    def generate_articles(self):
        articles_paths = glob.glob(self.configs.articles() + '*')

        for article_path in articles_paths:
            self._generate_article(article_path)


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
