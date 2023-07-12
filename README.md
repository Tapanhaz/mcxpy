
<div class="cell markdown">

***Experimental code to fetch data from mcx.*** ***Do not use this code
to programmatically get data from mcx exchange.*** ***This code is
uploaded here only for educational purpose.*** ***The uploader is not
liable for any type of damage caused by or arising from the use of this
code.***

Installation:

mcxpy installer is available on PyPI:

pip install mcxpy

</div>

<div class="cell code" execution_count="1">

``` python
from mcx import *
```

</div>

<div class="cell markdown">

***All Functions outputs are in pandas dataframe/datetime.datetime***

1.  mcx_bhavcopy(bhavdate)

    Fetch the bhacopy of the given date

2.  mcx_circulars(from_date, to_date)

    Fetch Circulars. By default it will return last 4 days circulars.

\*\*\*Below Functions names are self-explanatory.

1.  mcx_marketwatch()

2.  mcx_topgainers()

3.  mcx_toploosers()

4.  mcx_mostactiveoptions()

5.  mcx_mostactivecontracts()

6.  mcx_heatmap()

7.  mcx_expiry(commodity, instrument, expirytype)

    By defaults, it returns the current expiry of Crudeoil options

</div>

<div class="cell code" execution_count="13">

``` python
mcx_expiry()
```

<div class="output execute_result" execution_count="13">

    datetime.datetime(2023, 7, 17, 0, 0)

</div>

</div>

<div class="cell code" execution_count="14">

``` python
mcx_expiry(commodity='NATURALGAS',instrument='future',expirytype='current')
```

<div class="output execute_result" execution_count="14">

    datetime.datetime(2023, 7, 26, 0, 0)

</div>

</div>

<div class="cell markdown">

1.  mcx_optionchain(commodity, expiry)

    Fetch the optionchain.

2.  mcx_pcr(expirywise)

    Returns the pcr. By default expirywise is False (Returns
    commoditywise pcr)

3.  mcx_icomdexindices(datatype,start_date, end_date)

    start_date and end_date are needed only for historical datatype. By
    defaults returns today's data

12 mcx_quote(commodity,instrument, expiry, optiontype, strikeprice,
outputtype)

    Fetch quote of the given commodity. optiontype and strikeprice needed only for option instrument.

</div>
