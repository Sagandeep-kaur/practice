import pytest
from selenium import webdriver
from Pages.Pos import Pos
#pytest -o log_cli=true
from Pages.Station import Station
from Pages.Login import Loginpage
from Pages.OrderQueue import OrderQueue
from Utilities.Utils import Utils
import time
import re
#import softest
#from Utilities.Baseclass import baseclass
#from ddt import ddt, data, unpack
import unittest

@pytest.mark.usefixtures("setup")
class TestCaseone(unittest.TestCase):
    log = Utils.custom_logger()

    Customer_Name = "Sagan"
    product = "Banana Split"
    size = "Small"
    ingredient_one = "Soymilk"
    ingredient_two = "2% Milk"
    ingredient_three = "Chocolate Powder"
    key = "y"


    @pytest.fixture(autouse=True)
    def class_setup(self):
        self.lp = Pos(self.browser,self.wait)
        self.sp = Station(self.browser,self.wait)
        self.cp = Loginpage(self.browser, self.wait)
        self.oq = OrderQueue(self.browser,self.wait)
        #self.ut = Utils(self.browser)


    def clickOrderName(self):

        j = 0
        # clicking on order
        while j < 5:
            try:
                self.lp.clickOrdername()
                break

            except:
                self.browser.refresh()
                self.lp.select_order(self.product, self.size, self.Customer_Name)
            j = j + 1
        time.sleep(2)


    def test_AorderCreate(self):
        global qty_one, qty_two, qty_three

        self.cp.Login("pos","pos")
        self.lp.select_order(self.product, self.size, self.Customer_Name)
        self.clickOrderName()
        qty_one = self.lp.getIngredientQty(self.ingredient_one)
        qty_two = self.lp.getIngredientQty(self.ingredient_two)
        qty_three = self.lp.getIngredientQty(self.ingredient_three)

        # select modification ingredient 1
        self.lp.select_Modif(self.ingredient_one, "LIGHT")

        # select modification ingredient 2
        self.lp.select_Modif(self.ingredient_two, "SUB")

        # select modification ingredient 3
        self.lp.select_Modif(self.ingredient_three, "STANDARD")
        self.lp.clickCrossButton()
        self.lp.createOrder()

    def test_BCustomerName(self):
        flag = False
        global Order_Number
        self.cp.Login("order_queue", "qq")
        time.sleep(25)
        card_list = self.oq.GetOrderCardList()
        for card in card_list:

            if TestCaseone.Customer_Name in card.text:
                flag = True
                print("order name verified")
                self.log.info("order name verified")
        if flag == False:
            raise Exception("order name not in order queue")
        Order_Number = self.oq.GetOrderNumber(self.Customer_Name)


    def test_CStationOneOrderInfo(self):
        global StartTime
        self.cp.Login("station1", "s1")
        self.sp.scanCode(self.key)
        time.sleep(6)
        StartTime = self.sp.getStartTime()
        station_Name = self.sp.getStation_Name()
        ProductNameOnScreen  = self.sp.getProductNameOnScreen()
        OrderSizeOnScreen = self.sp.getOrderSizeOnScreen()
        CustomerNameOnScreen = self.sp.getCustomerNameOnScreen()
        orderNo = self.sp.getorderNo()

        JarImage = self.sp.getJarImage()
        assert JarImage.is_displayed() == True
        list = re.findall(r'#\d+', orderNo)
        orderNo = "".join(list)
        text = self.sp.getText()
        qty_Light = self.sp.GetQtyOnStation(TestCaseone.ingredient_one, text)
        print(qty_Light)
        qty_sub = self.sp.GetQtyOnStation(TestCaseone.ingredient_two, text)
        qty_Standard = self.sp.GetQtyOnStation(TestCaseone.ingredient_three, text)
        time.sleep(3)
        assert station_Name == "LIQUID"
        assert self.product == ProductNameOnScreen
        assert self.size == OrderSizeOnScreen
        assert Order_Number == orderNo
        assert self.Customer_Name == CustomerNameOnScreen

        # asserting whether ingredient chosen earlier and modified to "light" has correct qty:
        assert int(qty_Light) == int(qty_one/2)

        assert int(qty_sub) == int(qty_one/2) + int(qty_two)

        assert int(qty_Standard) == int(qty_three)

        self.sp.logout()
        self.browser.refresh()

    def test_DStationFiveOrderInfo(self):

        self.cp.Login("station5", "s5")
        self.sp.scanCode(self.key)
        time.sleep(8)
        station_Name = self.sp.getStation_Name()
        StationFive_Text = self.sp.gettext()

        Endtime = self.sp.getEndTime()

        assert station_Name == "POUR"
        assert Endtime != StartTime
        Size = self.size.upper()
        str2 = self.Customer_Name + "," + "\n" + "your" + "\n" + Size + "\n" + self.product + "\n" + "is ready!"

        if str2 in StationFive_Text:
            self.log.info("end message verified successfully")
        else:
            self.log.info("end message verification failed")
        self.sp.logout()
        self.browser.refresh()

    def test_EOrderDisappearsfromQueue(self):

        self.cp.Login("order_queue","qq")
        # logging into order queue again to verify if the scanned out order disappears or not
        time.sleep(25)
        BodyText = self.oq.GetBodyText()

        if Order_Number in BodyText:
           #print("order queue verification failed after completing order")
           self.log.info("order queue verification failed after completing order")

        else:
           #print("order queue verification passed after completing order")
           self.log.info("order queue verification passed after completing order")


