# SQL Queries and Outputs

## q1_select_where

```sql
SELECT title, price_gbp, price_inr, in_stock
FROM books
WHERE in_stock = 1
ORDER BY title;
```

```text
                                                                                            title  price_gbp  price_inr  in_stock
                                                               1,000 Places to See Before You Die      26.08    2751.44         1
                                                              1st to Die (Women's Murder Club #1)      53.98    5694.89         1
                                                          A Flight of Arrows (The Pathfinders #2)      55.53    5858.42         1
                                                                                 A Murder in Time      16.64    1755.52         1
                                                                                A Paris Apartment      39.01    4115.55         1
                                                A Spy's Devotion (The Regency Spies of London #1)      16.97    1790.33         1
                                                          A Study in Scarlet (Sherlock Holmes #1)      16.73    1765.02         1
                                                                               A Summer In Europe      44.34    4677.87         1
                                                           A Time of Torment (Charlie Parker #14)      48.35    5100.92         1
                                                                 A Year in Provence (Provence #1)      56.88    6000.84         1
                                                                           Between Shades of Gray      20.79    2193.34         1
                                                             Blood Defense (Samantha Brinkman #1)      20.30    2141.65         1
                                                                    Boar Island (Anna Pigeon #19)      59.48    6275.14         1
                                                              Career of Evil (Cormoran Strike #3)      24.72    2607.96         1
                                                 Delivering the Truth (Quaker Midwife Mystery #1)      20.89    2203.90         1
                                                               Extreme Prey (Lucas Davenport #26)      25.40    2679.70         1
                        Forever and Forever: The Courtship of Henry Longfellow and Fanny Appleton      29.69    3132.30         1
                               Full Moon over Noahâs Ark: An Odyssey to Mount Ararat and Beyond      49.43    5214.86         1
                                                                        Girl With a Pearl Earring      26.77    2824.24         1
                                                                            Girl in the Blue Coat      46.83    4940.56         1
                                                  Glory over Everything: Beyond The Kitchen House      45.84    4836.12         1
                                                                       Hide Away (Eve Duncan #20)      11.84    1249.12         1
                                                                             In a Dark, Dark Wood      19.63    2070.96         1
                                                            In the Woods (Dublin Murder Squad #1)      38.38    4049.09         1
                                                                          It's Only the Himalayas      45.17    4765.44         1
                                                                                      Lilac Girls      17.28    1823.04         1
                                                                            Lost Among the Living      27.70    2922.35         1
                                                                             Love, Lies and Spies      20.55    2168.02         1
                                                                                      Most Wanted      35.28    3722.04         1
                                                                                     Mrs. Houdini      30.25    3191.38         1
                                            Murder at the 42nd Street Library (Raymond Ambler #1)      54.36    5734.98         1
                                                        Neither Here nor There: Travels in Europe      38.95    4109.23         1
                                                                                Playing with Fire      13.71    1446.41         1
                                                                 Poisonous (Max Revere Novels #3)      26.80    2827.40         1
                               See America: A Celebration of Our National Parks & Treasured Sites      48.87    5155.78         1
                                                                                    Sharp Objects      47.82    5045.01         1
                                                                                         Starlark      25.83    2725.06         1
                                                             Tastes Like Fear (DI Marnie Rome #3)      10.69    1127.79         1
                                                           That Darkness (Gardiner and Renner #1)      13.92    1468.56         1
                         The Bachelor Girl's Guide to Murder (Herringford and Watts Mysteries #1)      52.30    5517.65         1
                                                       The Constant Princess (The Tudor Court #1)      16.62    1753.41         1
                                                        The Cuckoo's Calling (Cormoran Strike #1)      19.21    2026.66         1
                                                                                       The Exiled      43.45    4583.98         1
                                                        The Girl In The Ice (DCI Erika Foster #1)      15.85    1672.18         1
                                                                                The Girl You Lost      12.29    1296.59         1
                                                                         The Great Railway Bazaar      30.54    3221.97         1
                                                The Guernsey Literary and Potato Peel Pie Society      49.53    5225.42         1
                                                                            The House by the Lake      36.95    3898.23         1
                                                                           The Invention of Wings      37.34    3939.37         1
                                                                   The Last Mile (Amos Decker #2)      54.21    5719.16         1
                                                                 The Last Painting of Sara de Vos      55.55    5860.52         1
                                                                        The Marriage of Opposites      28.08    2962.44         1
                                                  The Murder of Roger Ackroyd (Hercule Poirot #4)      44.10    4652.55         1
                                              The Mysterious Affair at Styles (Hercule Poirot #1)      24.80    2616.40         1
                           The No. 1 Ladies' Detective Agency (No. 1 Ladies' Detective Agency #1)      57.70    6087.35         1
                                                                            The Passion of Dolssa      28.32    2987.76         1
                                                                              The Past Never Ends      56.50    5960.75         1
                                                                                     The Red Tent      35.66    3762.13         1
The Road to Little Dribbling: Adventures of an American in Britain (Notes From a Small Island #2)      23.21    2448.66         1
                                                                                The Secret Healer      34.56    3646.08         1
                                                                The Silkworm (Cormoran Strike #2)      23.05    2431.78         1
                                                                                        The Widow      27.26    2875.93         1
                                                                               Tipping the Velvet      53.74    5669.57         1
                                                                             Under the Tuscan Sun      37.33    3938.31         1
                              Vagabonding: An Uncommon Guide to the Art of Long-Term World Travel      36.94    3897.17         1
                                                                           Voyager (Outlander #3)      21.07    2222.89         1
                                What Happened on Beale Street (Secrets of the South Mysteries #2)      25.37    2676.54         1
                                                                              While You Were Mine      41.32    4359.26         1
                                                  World Without End (The Pillars of the Earth #2)      32.97    3478.34         1
```

## q2_order_by_limit

```sql
SELECT title, rating, price_gbp, price_inr
FROM books
ORDER BY rating DESC, price_gbp DESC
LIMIT 10;
```

```text
                                                                   title  rating  price_gbp  price_inr
                                 A Flight of Arrows (The Pathfinders #2)       5      55.53    5858.42
The Bachelor Girl's Guide to Murder (Herringford and Watts Mysteries #1)       5      52.30    5517.65
                                  A Time of Torment (Charlie Parker #14)       5      48.35    5100.92
                                                     While You Were Mine       5      41.32    4359.26
                                                            The Red Tent       5      35.66    3762.13
                                                            Mrs. Houdini       5      30.25    3191.38
                                                   The Passion of Dolssa       5      28.32    2987.76
                                      1,000 Places to See Before You Die       5      26.08    2751.44
       What Happened on Beale Street (Secrets of the South Mysteries #2)       5      25.37    2676.54
                                       The Silkworm (Cormoran Strike #2)       5      23.05    2431.78
```

## q3_distinct

```sql
SELECT DISTINCT category_name
FROM categories
ORDER BY category_name;
```

```text
     category_name
Historical Fiction
           Mystery
            Travel
```

## q4_between

```sql
SELECT title, price_gbp, rating
FROM books
WHERE price_gbp BETWEEN 20 AND 40
ORDER BY price_gbp, title;
```

```text
                                                                                            title  price_gbp  rating
                                                             Blood Defense (Samantha Brinkman #1)      20.30       3
                                                                             Love, Lies and Spies      20.55       2
                                                                           Between Shades of Gray      20.79       5
                                                 Delivering the Truth (Quaker Midwife Mystery #1)      20.89       4
                                                                           Voyager (Outlander #3)      21.07       5
                                                                The Silkworm (Cormoran Strike #2)      23.05       5
The Road to Little Dribbling: Adventures of an American in Britain (Notes From a Small Island #2)      23.21       1
                                                              Career of Evil (Cormoran Strike #3)      24.72       2
                                              The Mysterious Affair at Styles (Hercule Poirot #1)      24.80       4
                                What Happened on Beale Street (Secrets of the South Mysteries #2)      25.37       5
                                                               Extreme Prey (Lucas Davenport #26)      25.40       3
                                                                                         Starlark      25.83       3
                                                               1,000 Places to See Before You Die      26.08       5
                                                                        Girl With a Pearl Earring      26.77       1
                                                                 Poisonous (Max Revere Novels #3)      26.80       3
                                                                                        The Widow      27.26       2
                                                                            Lost Among the Living      27.70       4
                                                                        The Marriage of Opposites      28.08       4
                                                                            The Passion of Dolssa      28.32       5
                        Forever and Forever: The Courtship of Henry Longfellow and Fanny Appleton      29.69       3
                                                                                     Mrs. Houdini      30.25       5
                                                                         The Great Railway Bazaar      30.54       1
                                                  World Without End (The Pillars of the Earth #2)      32.97       4
                                                                                The Secret Healer      34.56       3
                                                                                      Most Wanted      35.28       3
                                                                                     The Red Tent      35.66       5
                              Vagabonding: An Uncommon Guide to the Art of Long-Term World Travel      36.94       2
                                                                            The House by the Lake      36.95       1
                                                                             Under the Tuscan Sun      37.33       3
                                                                           The Invention of Wings      37.34       1
                                                            In the Woods (Dublin Murder Squad #1)      38.38       2
                                                        Neither Here nor There: Travels in Europe      38.95       3
                                                                                A Paris Apartment      39.01       4
```

## q5_in

```sql
SELECT title, rating, in_stock
FROM books
WHERE rating IN (4, 5)
ORDER BY rating DESC, title;
```

```text
                                                                   title  rating  in_stock
                                      1,000 Places to See Before You Die       5         1
                                 A Flight of Arrows (The Pathfinders #2)       5         1
                       A Spy's Devotion (The Regency Spies of London #1)       5         1
                                  A Time of Torment (Charlie Parker #14)       5         1
                                                  Between Shades of Gray       5         1
                                                            Mrs. Houdini       5         1
The Bachelor Girl's Guide to Murder (Herringford and Watts Mysteries #1)       5         1
                                                       The Girl You Lost       5         1
                                                   The Passion of Dolssa       5         1
                                                            The Red Tent       5         1
                                       The Silkworm (Cormoran Strike #2)       5         1
                                                  Voyager (Outlander #3)       5         1
       What Happened on Beale Street (Secrets of the South Mysteries #2)       5         1
                                                     While You Were Mine       5         1
                                                       A Paris Apartment       4         1
                                        A Year in Provence (Provence #1)       4         1
                        Delivering the Truth (Quaker Midwife Mystery #1)       4         1
      Full Moon over Noahâs Ark: An Odyssey to Mount Ararat and Beyond       4         1
                                                   Lost Among the Living       4         1
                   Murder at the 42nd Street Library (Raymond Ambler #1)       4         1
                                                           Sharp Objects       4         1
                                               The Marriage of Opposites       4         1
                         The Murder of Roger Ackroyd (Hercule Poirot #4)       4         1
                     The Mysterious Affair at Styles (Hercule Poirot #1)       4         1
  The No. 1 Ladies' Detective Agency (No. 1 Ladies' Detective Agency #1)       4         1
                                                     The Past Never Ends       4         1
                         World Without End (The Pillars of the Earth #2)       4         1
```

## q6_join

```sql
SELECT
    c.category_name,
    b.title,
    b.rating,
    b.price_inr
FROM books AS b
INNER JOIN categories AS c
    ON b.category_id = c.category_id
ORDER BY b.rating DESC, b.price_inr DESC, b.title
LIMIT 10;
```

```text
     category_name                                                                    title  rating  price_inr
Historical Fiction                                  A Flight of Arrows (The Pathfinders #2)       5    5858.42
           Mystery The Bachelor Girl's Guide to Murder (Herringford and Watts Mysteries #1)       5    5517.65
           Mystery                                   A Time of Torment (Charlie Parker #14)       5    5100.92
Historical Fiction                                                      While You Were Mine       5    4359.26
Historical Fiction                                                             The Red Tent       5    3762.13
Historical Fiction                                                             Mrs. Houdini       5    3191.38
Historical Fiction                                                    The Passion of Dolssa       5    2987.76
            Travel                                       1,000 Places to See Before You Die       5    2751.44
           Mystery        What Happened on Beale Street (Secrets of the South Mysteries #2)       5    2676.54
           Mystery                                        The Silkworm (Cormoran Strike #2)       5    2431.78
```

## JOIN equivalence

### SQL JOIN result

```text
     category_name                                                                    title  rating  price_inr
Historical Fiction                                  A Flight of Arrows (The Pathfinders #2)       5    5858.42
           Mystery The Bachelor Girl's Guide to Murder (Herringford and Watts Mysteries #1)       5    5517.65
           Mystery                                   A Time of Torment (Charlie Parker #14)       5    5100.92
Historical Fiction                                                      While You Were Mine       5    4359.26
Historical Fiction                                                             The Red Tent       5    3762.13
Historical Fiction                                                             Mrs. Houdini       5    3191.38
Historical Fiction                                                    The Passion of Dolssa       5    2987.76
            Travel                                       1,000 Places to See Before You Die       5    2751.44
           Mystery        What Happened on Beale Street (Secrets of the South Mysteries #2)       5    2676.54
           Mystery                                        The Silkworm (Cormoran Strike #2)       5    2431.78
```

### pandas.merge result

```text
     category_name                                                                    title  rating  price_inr
Historical Fiction                                  A Flight of Arrows (The Pathfinders #2)       5    5858.42
           Mystery The Bachelor Girl's Guide to Murder (Herringford and Watts Mysteries #1)       5    5517.65
           Mystery                                   A Time of Torment (Charlie Parker #14)       5    5100.92
Historical Fiction                                                      While You Were Mine       5    4359.26
Historical Fiction                                                             The Red Tent       5    3762.13
Historical Fiction                                                             Mrs. Houdini       5    3191.38
Historical Fiction                                                    The Passion of Dolssa       5    2987.76
            Travel                                       1,000 Places to See Before You Die       5    2751.44
           Mystery        What Happened on Beale Street (Secrets of the South Mysteries #2)       5    2676.54
           Mystery                                        The Silkworm (Cormoran Strike #2)       5    2431.78
```

Equivalent: `True`
