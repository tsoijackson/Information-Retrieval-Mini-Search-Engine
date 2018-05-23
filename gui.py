from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

TEST_RESULTS = ['link1', 'link2', 'link3', 'link4', 'link5']

def test():
    pass

class Link(Label):
    def __init__(self, rank:int, link:str):
        super(Link, self).__init__()
        self.text_size = self.size
        self.halign = 'left'
        self.valign = 'middle'
        self.text = "{}     {}".format(str(rank), link)

class SearchBar(BoxLayout):
    def __init__(self, **kwargs):
        super(SearchBar, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.button = Button(text='Search', font_size=25, size_hint=(0.4,1))

        self.add_widget(TextInput(multiline=False, font_size=20))
        self.add_widget(self.button)


class GuiLayout(GridLayout):
    def __init__(self, **kwargs):
        super(GuiLayout, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 12

        #Binding Search Button to run Search Engine
        self.searchBar = SearchBar()
        self.searchBar.button.bind(on_press=self.runSearchEngine)

        self.add_widget(Label(text='ICS Mini Search Engine', font_size=25))
        self.add_widget(self.searchBar)
        self.add_links(TEST_RESULTS)

    def add_links(self, linksList: [str]):
        #If there are less than 10 links, fill list up with None
        while len(linksList) < 10:
            linksList.append(None)

        for n,link in enumerate(linksList):
            if link == None:
                self.add_widget(Link(n, "No Link"))
            else:
                self.add_widget(Link(n, link))

    def runSearchEngine(self, instance):
        print('Beginning to run Search Engine...')


class SearchEngineGui(App):
    def build(self):
        return GuiLayout()

if __name__ == '__main__':
    SearchEngineGui().run()