# Titanic EDA Report

## Dataset profile

### Shape
(891, 15)

### Info
```text
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 891 entries, 0 to 890
Data columns (total 15 columns):
 #   Column       Non-Null Count  Dtype   
---  ------       --------------  -----   
 0   survived     891 non-null    int64   
 1   pclass       891 non-null    int64   
 2   sex          891 non-null    object  
 3   age          714 non-null    float64 
 4   sibsp        891 non-null    int64   
 5   parch        891 non-null    int64   
 6   fare         891 non-null    float64 
 7   embarked     889 non-null    object  
 8   class        891 non-null    category
 9   who          891 non-null    object  
 10  adult_male   891 non-null    bool    
 11  deck         203 non-null    category
 12  embark_town  889 non-null    object  
 13  alive        891 non-null    object  
 14  alone        891 non-null    bool    
dtypes: bool(2), category(2), float64(2), int64(4), object(5)
memory usage: 80.7+ KB

```

### Describe
```text
          survived      pclass   sex         age       sibsp       parch        fare embarked  class  who adult_male deck  embark_town alive alone
count   891.000000  891.000000   891  714.000000  891.000000  891.000000  891.000000      889    891  891        891  203          889   891   891
unique         NaN         NaN     2         NaN         NaN         NaN         NaN        3      3    3          2    7            3     2     2
top            NaN         NaN  male         NaN         NaN         NaN         NaN        S  Third  man       True    C  Southampton    no  True
freq           NaN         NaN   577         NaN         NaN         NaN         NaN      644    491  537        537   59          644   549   537
mean      0.383838    2.308642   NaN   29.699118    0.523008    0.381594   32.204208      NaN    NaN  NaN        NaN  NaN          NaN   NaN   NaN
std       0.486592    0.836071   NaN   14.526497    1.102743    0.806057   49.693429      NaN    NaN  NaN        NaN  NaN          NaN   NaN   NaN
min       0.000000    1.000000   NaN    0.420000    0.000000    0.000000    0.000000      NaN    NaN  NaN        NaN  NaN          NaN   NaN   NaN
25%       0.000000    2.000000   NaN   20.125000    0.000000    0.000000    7.910400      NaN    NaN  NaN        NaN  NaN          NaN   NaN   NaN
50%       0.000000    3.000000   NaN   28.000000    0.000000    0.000000   14.454200      NaN    NaN  NaN        NaN  NaN          NaN   NaN   NaN
75%       1.000000    3.000000   NaN   38.000000    1.000000    0.000000   31.000000      NaN    NaN  NaN        NaN  NaN          NaN   NaN   NaN
max       1.000000    3.000000   NaN   80.000000    8.000000    6.000000  512.329200      NaN    NaN  NaN        NaN  NaN          NaN   NaN   NaN
```

## Missing-value percentages before cleaning
|             |   missing_percent |
|:------------|------------------:|
| age         |           19.8653 |
| embarked    |            0.2245 |
| deck        |           77.2166 |
| embark_town |            0.2245 |

## Cleaning decisions
| column      |   missing_percent | strategy                | reason                                                                                               |
|:------------|------------------:|:------------------------|:-----------------------------------------------------------------------------------------------------|
| deck        |           77.2166 | drop_column             | >30% missing; imputation would be unreliable                                                         |
| embarked    |            0.2245 | drop_rows               | <5% missing; dropped rows affected by this column (total rows dropped across low-missing columns: 2) |
| embark_town |            0.2245 | drop_rows               | <5% missing; dropped rows affected by this column (total rows dropped across low-missing columns: 2) |
| age         |           19.8653 | median_impute (28.0000) | 5%–30% missing; imputation required                                                                  |

Cleaned dataset shape: **(889, 14)**

## Univariate analysis
- `age` IQR bounds: [2.500, 54.500]. Outlier count: **65**.
- `fare` IQR bounds: [-26.761, 65.656]. Outlier count: **114**.
- Fare mean = **32.097**, median = **14.454**, mode = **8.050**. Because the ordering is mean > median and median > mode, `fare` is interpreted as **right-skewed**.

## Bivariate survival rates
### By sex
| sex    |   survival_rate_percent |
|:-------|------------------------:|
| female |                   74.04 |
| male   |                   18.89 |

### By pclass
|   pclass |   survival_rate_percent |
|---------:|------------------------:|
|        1 |                   62.62 |
|        2 |                   47.28 |
|        3 |                   24.24 |

### By sex and pclass
|               |   survival_rate_percent |
|:--------------|------------------------:|
| ('female', 1) |                   96.74 |
| ('female', 2) |                   92.11 |
| ('female', 3) |                   50    |
| ('male', 1)   |                   36.89 |
| ('male', 2)   |                   15.74 |
| ('male', 3)   |                   13.54 |

### Correlation matrix
|          |   survived |   pclass |    age |   sibsp |   parch |   fare |
|:---------|-----------:|---------:|-------:|--------:|--------:|-------:|
| survived |      1     |   -0.336 | -0.07  |  -0.034 |   0.083 |  0.255 |
| pclass   |     -0.336 |    1     | -0.337 |   0.082 |   0.017 | -0.548 |
| age      |     -0.07  |   -0.337 |  1     |  -0.233 |  -0.171 |  0.094 |
| sibsp    |     -0.034 |    0.082 | -0.233 |   1     |   0.415 |  0.161 |
| parch    |      0.083 |    0.017 | -0.171 |   0.415 |   1     |  0.218 |
| fare     |      0.255 |   -0.548 |  0.094 |   0.161 |   0.218 |  1     |

### Two strongest absolute off-diagonal correlations
- **pclass vs fare: r = -0.548** (|r| = 0.548), a negative relationship.
- **sibsp vs parch: r = 0.415** (|r| = 0.415), a positive relationship.

Boolean mask sanity checks: female passenger rows = 312; male passenger rows = 577.

## Multivariate data story
### 1. Survival rate by sex

The bar chart shows a clear difference in survival rates between female and male passengers. This indicates that sex is strongly associated with the target and should remain in the predictive feature set.
### 2. Survival rate by passenger class

Survival rate changes substantially across passenger classes. Passenger class therefore provides a second important signal that complements sex and helps explain differences in outcomes.
### 3. Fare distribution by sex and class

Fare varies by passenger class, and the class composition differs by sex. This provides a multivariate view of the socioeconomic structure underlying the passenger records and explains why fare can add predictive information beyond the class label alone.
### 4. Age vs fare with survival and sex

The scatter plot combines age, fare, survival, and sex to show how several variables interact instead of looking at one pair at a time. Survival observations are distributed differently across the age/fare space, reinforcing the need for a multivariate model rather than a single-rule explanation.

## Exploratory z-score standardization
The following check is performed on the full cleaned DataFrame only for EDA sanity checking. It is not reused by the modeling pipeline; the modeling pipeline performs its own train-only scaling.
| column   |   before_mean |   before_std |   after_mean |   after_std |
|:---------|--------------:|-------------:|-------------:|------------:|
| age      |       29.3152 |      12.9849 |            0 |           1 |
| fare     |       32.0967 |      49.6975 |            0 |           1 |

## Saved artifacts

- `titanic.csv` — raw offline fallback created immediately after the one network/cache load.
- `titanic_cleaned.csv` — cleaned continuation dataset consumed by `02_modeling.py`.
- `outputs/` — tables, charts, missingness decisions, and the written EDA interpretation.
