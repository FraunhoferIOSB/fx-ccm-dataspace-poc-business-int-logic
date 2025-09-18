import asyncio
import logging

from asyncua import Server, ua
from asyncua.common.methods import uamethod
import requests

from datetime import datetime, timedelta, timezone

class Channel:
    def __init__(self, endPoint, opcuaName):
        self._endPoint = endPoint
        self._opcuaName = opcuaName
        self._node = None

    @property
    def endPoint(self):
        return self._endPoint    
        
    @property
    def opcuaName(self):
        return self._opcuaName
    
    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, value): 
        self._node = value


# select Value configuration
publishingInterval = 1  # Interval in seconds
# timedelta where data is not published 
dataTimeout = 100000000

_logger = logging.getLogger(__name__)

def readOneChannel(channel):

    url = "http://MX-Adapter-Data-Source:8000" + channel.endPoint

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        data = response.json()
        _logger.info("Name: %s", channel.opcuaName)
        _logger.info("Value: %s", data['Value'])
        _logger.info("Timestamp: %s", data['Timestamp'])
        value = data['Value']
        date = data['Timestamp']
        status = ua.StatusCode(ua.StatusCodes.Good)

    except requests.exceptions.RequestException as e:
        print(f"Error accessing the API: {e}")
        value = 0
        date = ""
        status = ua.StatusCode(ua.StatusCodes.BadDataUnavailable)

    return value, date, status

async def main():

    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # set up our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    channelList = []
    channelList.append(Channel("/fx/gen/Temperature", "temperature"))
    channelList.append(Channel("/fx/gen/Current", "current"))
    channelList.append(Channel("/fx/gen/Speed", "speed"))

    myobj = await server.nodes.objects.add_object(idx, "axis")
    
    for channel in channelList:
        node = await myobj.add_variable(idx, channel.opcuaName, 0.0)
        channel.node = node
    
    myobj = await server.nodes.objects.add_object(idx, "SyncCounter")
    SyncCounterVar = await myobj.add_variable(idx, "SyncCounter", 0)
    res = ua.DataValue(Value=99, StatusCode_= ua.StatusCode(ua.StatusCodes.GoodNoData))
    await SyncCounterVar.write_value(res)
    
    test_val = 0   
    
    await SyncCounterVar.write_value(test_val)

    _logger.info("Starting server!")
    async with server:
        
        while True:
            start_time = asyncio.get_event_loop().time()
            
            for channel in channelList:
                value, date_string, status = readOneChannel(channel)
                #print(date_string)
                if status == ua.StatusCode(ua.StatusCodes.Good):
                    date_format = "%Y-%m-%d %H:%M:%S"
                    dt_object = datetime.strptime(date_string, date_format) 
                    dt_object = dt_object.replace(tzinfo=timezone.utc)

                    # Get the current time in UTC
                    currentDateTime = datetime.now(timezone.utc)

                    if dt_object > currentDateTime - timedelta(seconds=dataTimeout):

                        #if "_Temp" in channel.influxName:
                        if (test_val% 2) == 0:
                            value += 0.000000001
                        res = ua.DataValue(Value=float(value), StatusCode_= status, SourceTimestamp=currentDateTime)
                        _logger.info("Set value of %s to %.1f Time: %s", channel.endPoint, value, str(datetime.now(timezone.utc)))
                        await channel.node.write_value(res)
            
            test_val += 1
            res = ua.DataValue(Value=test_val, StatusCode_= ua.StatusCode(ua.StatusCodes.Good))
            await SyncCounterVar.write_value(res)
            
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time > publishingInterval:
                print(f"Warning: Processing time {elapsed_time:.2f}s exceeded the interval of {publishingInterval}s.")
            
            sleep_time = max(0, publishingInterval - elapsed_time)
            await asyncio.sleep(sleep_time)



if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.WARNING)
    asyncio.run(main(), debug=False)
    
