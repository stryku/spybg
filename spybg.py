import ntpath
import sys, glob


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


class Templates:
    def __init__(self):
        self.index_path = ''
        self.article_path = ''

    @staticmethod
    def _find_template(configs, pattern):
        found = glob.glob(configs.templates() + pattern + '.spybgt')
        if len(found) == 0:
            raise Exception('No index template found in: ' + configs.templates())

        if len(found) > 1:
            raise Exception('Multiple index templates found: ' + str(found))

        return found[0]

    @staticmethod
    def build(configs):
        templates = Templates()
        templates.index_path = Templates._find_template(configs, 'index.*')
        templates.article_path = Templates._find_template(configs, 'article.*')
        return templates

    def output_index_name(self):
        return ntpath.basename(self.index_path).replace('.spybgt', '')


class ArticlesGenerator:
    def generate_articles_list(self):
        return 'Articles list'


class Spybg:
    def __init__(self):
        self.configs = Configs()
        self.templates = Templates.build(self.configs)
        self.articles_generator = ArticlesGenerator()

    def generate(self):
        with open(self.templates.index_path, 'r') as file:
            index_template = file.read()

        generated_index = index_template.replace('%SPYBG_ARTICLES_LIST%', self.articles_generator.generate_articles_list())

        with open(self.configs.output_index(self.templates.output_index_name()), 'w+') as file:
            file.write(generated_index)


def main():
    spybg = Spybg()
    spybg.generate()


if __name__ == "__main__":
    main()
