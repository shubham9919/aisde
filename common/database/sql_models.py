from passlib.context import CryptContext
from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    MetaData,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import sessionmaker

from common.config_constants import (
    BUNDLE_API_METADATA_TABLENAME,
    REGISTERED_CLIENT_DATA_TABLENAME,
    CLIENT_LOGIN_TABLENAME,
    CLIENT_VENDORS_RELATIONSHIP_FOR_UI_TABLENAME,
    CYBER_SCHEMA_NAME,
    DOMAIN_API_METADATA_TABLENAME,
    GENERAL_COMPANY_DATA_TABLENAME,
    NVD_DATA_TABLENAME,
    MODEL_PREDICTED_WEBSITE_FEATURES_DATA_TABLENAME,
    RESULT_DATA_TABLENAME,
    SPECIFIC_COMPANY_DATA,
    TOP_CVE_DATA_TABLENAME,
    MODEL_PREDICTED_WEBSITE_FEATURES_DATA_TABLENAME,
    VENDOR_AND_CLIENT_TABLENAME,
    VENDOR_RISK_DATA_TABLENAME,
    WEBSITE_API_METADATA_TABLENAME,
    COMPANY_DOMAIN_DATA_TABLENAME,
)
from common.database.sql_database_connection import CyberDatabase

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000,
)


Base = declarative_base(metadata=MetaData(schema=CYBER_SCHEMA_NAME))
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=CyberDatabase().engine())
)
Base.query = db_session.query_property()


class NVDDatabase(Base):
    __tablename__ = NVD_DATA_TABLENAME
    cve = Column(String, primary_key=True)
    datetime_updated = Column(DateTime, primary_key=True, default=func.now())
    description = Column(String)
    technologies = Column(ARRAY(String))
    basescorev2 = Column(Float)
    exploitabilityscorev2 = Column(Float)
    impactscorev2 = Column(Float)
    basescorev3 = Column(Float)
    exploitabilityscorev3 = Column(Float)
    impactscorev3 = Column(Float)
    link = Column(String)


class TopCVETable(Base):
    __tablename__ = TOP_CVE_DATA_TABLENAME

    cve = Column(String, primary_key=True)
    datetime_updated = Column(DateTime, primary_key=True, default=func.now())
    current = Column(Float)
    previouslyexploited = Column(Float)
    highest = Column(Float)


class BundleApiMetadataTable(Base):
    __tablename__ = BUNDLE_API_METADATA_TABLENAME

    id = Column(BigInteger, autoincrement=True, primary_key=True)
    fetch_datetime = Column(DateTime, primary_key=True, default=func.now())
    total_data_fetched = Column(Integer)
    s3_bundle_api_json_storage_link = Column(String, unique=True)


class CompanyDomainDataTable(Base):
    __tablename__ = COMPANY_DOMAIN_DATA_TABLENAME

    company_id = Column(BigInteger(), autoincrement=True, primary_key=True)
    company_name = Column(String, nullable=False, index=True)
    domain_name = Column(String, nullable=False, index=True)
    __table_args__ = (
        UniqueConstraint(
            "company_name", "domain_name", name="uq_CompanyDomainDataTable"
        ),
    )


class RegisteredClientDataTable(Base):
    __tablename__ = REGISTERED_CLIENT_DATA_TABLENAME
    client_id = Column(
        BigInteger(), autoincrement=True, primary_key=True, nullable=False
    )
    client_name = Column(
        String(),
        nullable=False,
        index=True,
    )
    client_domain = Column(
        String(),
        nullable=False,
        index=True,
    )
    __table_args__ = (
        UniqueConstraint(
            "client_name", "client_domain", name="uq_RegisteredClientDataTable"
        ),
        ForeignKeyConstraint(
            ["client_name", "client_domain"],
            ["company_domain_data.company_name", "company_domain_data.domain_name"],
        ),
    )


class ClientLoginTable(Base):
    __tablename__ = CLIENT_LOGIN_TABLENAME

    id = Column(BigInteger(), autoincrement=True, primary_key=True)
    client_id = Column(
        BigInteger(),
        ForeignKey(RegisteredClientDataTable.client_id),
        index=True,
        nullable=False,
    )
    email_id = Column(String(), unique=True, nullable=False, index=True)
    hashed_password = Column("hashed_password", String(), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    def __init__(
        self, client_id, email_id, hashed_password, is_active=True, is_verified=False
    ) -> None:
        self.client_id = client_id
        self.email_id = email_id
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.is_verified = is_verified


class ClientVendorsRelationshipForUiTable(Base):
    __tablename__ = CLIENT_VENDORS_RELATIONSHIP_FOR_UI_TABLENAME
    client_id = Column(
        BigInteger(),
        ForeignKey(RegisteredClientDataTable.client_id, ondelete="CASCADE"),
        primary_key=True,
    )
    client_vendors_relationship = Column(
        "client_vendors_relationship", JSON(), nullable=False
    )


class VendorAndClientTable(Base):
    __tablename__ = VENDOR_AND_CLIENT_TABLENAME
    vendor_client_row_id = Column(BigInteger(), primary_key=True, autoincrement=True)
    vendor_id = Column(
        BigInteger(),
        ForeignKey(CompanyDomainDataTable.company_id, ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    client_id = Column(
        BigInteger(),
        ForeignKey(RegisteredClientDataTable.client_id, ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    __table_args__ = (
        UniqueConstraint("vendor_id", "client_id", name="uq_VendorAndClientTable"),
    )


class SpecificCompanyData(Base):
    __tablename__ = SPECIFIC_COMPANY_DATA
    vendor_client_row_id = Column(
        BigInteger(),
        ForeignKey(VendorAndClientTable.vendor_client_row_id, ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    technologies = Column(ARRAY(String))


class ResultTable(Base):
    __tablename__ = RESULT_DATA_TABLENAME

    vendor_client_row_id = Column(
        BigInteger(),
        ForeignKey(VendorAndClientTable.vendor_client_row_id, ondelete="CASCADE"),
        primary_key=True,
    )
    datetime_executed = Column(DateTime, primary_key=True, default=func.now())
    nvd_score = Column(Float)
    css_score = Column(Float)
    master_score = Column(Float)
    breach_risk_score = Column(Float)
    bss_score = Column(Float)
    bss = Column(Float)


class VendorRiskTable(Base):
    __tablename__ = VENDOR_RISK_DATA_TABLENAME

    vendor_client_row_id = Column(
        BigInteger(),
        ForeignKey(VendorAndClientTable.vendor_client_row_id, ondelete="CASCADE"),
        primary_key=True,
    )

    company = Column(String)
    domain = Column(String, unique=True)
    industry = Column(String)
    status = Column(String)
    alert_type = Column(String)


class GeneralCompanyDataTable(Base):
    __tablename__ = GENERAL_COMPANY_DATA_TABLENAME

    id = Column(BigInteger(), autoincrement=True, primary_key=True)
    company_id = Column(
        BigInteger(),
        ForeignKey(CompanyDomainDataTable.company_id, ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    datetime_fetched = Column(DateTime, nullable=False, default=func.now())
    activity = Column(String)
    analyticsid = Column(String)
    ascompany = Column(String)
    technologies = Column(ARRAY(String))
    asnumber = Column(Integer)
    changes = Column(Integer)
    cloudscore = Column(Integer)
    cocnumber = Column(String)
    company = Column(String)
    continent = Column(String)
    copyright = Column(Integer)
    country = Column(String)
    date = Column(DateTime)
    date_executed = Column(Date)
    dateadded = Column(DateTime)
    developed = Column(Boolean)
    dnsns = Column(ARRAY(String))
    dnssec = Column(Boolean)
    dnstxt = Column(ARRAY(String))
    domain = Column(String)
    domainlength = Column(Integer)
    ecommerce = Column(Boolean)
    ecommercequality = Column(Integer)
    eii = Column(Integer)
    eiidelta = Column(Integer)
    flash = Column(Boolean)
    forwarding = Column(ARRAY(String))
    forwardingcount = Column(Integer)
    grade = Column(Float)
    hostingcountry = Column(String)
    hostname = Column(String)
    htmlsize = Column(Integer)
    idn = Column(Boolean)
    incominglinks = Column(Integer)
    ip = Column(ARRAY(String))
    ipv6 = Column(ARRAY(String))
    keywords = Column(ARRAY(String))
    language = Column(ARRAY(String))
    loadtime = Column(Integer)
    maps = Column(ARRAY(String))
    mobile = Column(Boolean)
    multilanguage = Column(Boolean)
    mxdomain = Column(String)
    nameserver = Column(String)
    outgoinglinks = Column(Integer)
    pages = Column(Integer)
    pagesindexed = Column(Integer)
    pagetypes = Column(ARRAY(String))
    privacysensitive = Column(Boolean)
    registrar = Column(String)
    renderedcookiehostnames = Column(ARRAY(String))
    response = Column(String)
    scanrequestid = Column(Integer)
    securityscore = Column(Integer)
    seo = Column(Integer)
    seosummary = Column(String)
    serversignature = Column(String)
    siccode = Column(Integer)
    sicdivision = Column(String)
    sicmajorgroup = Column(String)
    since = Column(DateTime)
    ssl = Column(Boolean)
    sslenddate = Column(DateTime)
    sslissuercommonname = Column(String)
    sslissuerorganization = Column(String)
    sslstartdate = Column(DateTime)
    ssltype = Column(String)
    status = Column(Integer)
    statuscodes = Column(ARRAY(Integer))
    subdomain = Column(String)
    subdomains = Column(ARRAY(String))
    subdomainscount = Column(Integer)
    title = Column(String)
    tld = Column(String)
    tldsuggestions = Column(ARRAY(String))
    tldtype = Column(String)
    trafficcountries = Column(ARRAY(String))
    trafficcrossborder = Column(Boolean)
    trafficindex = Column(BigInteger)
    trustgrade = Column(String)
    trustscore = Column(Integer)
    type = Column(String)
    visitors = Column(BigInteger)
    visitors_count = Column(BigInteger)
    visitorsavg = Column(BigInteger)
    visitorsavg_count = Column(BigInteger)
    websiteage = Column(Integer)
    websiteheaders = Column(ARRAY(String))
    websitestate = Column(ARRAY(String))
    wordcount = Column(Integer)
    zone = Column(Boolean)


class ModelPredictedWebsiteFeaturesDataTable(Base):
    __tablename__ = MODEL_PREDICTED_WEBSITE_FEATURES_DATA_TABLENAME

    general_company_features_row_id = Column(
        BigInteger(),
        ForeignKey(GeneralCompanyDataTable.id, ondelete="CASCADE"),
        primary_key=True,
    )
    datetime_executed = Column(DateTime, primary_key=True, default=func.now())
    date_executed = Column(Date, default=func.date(func.now()))
    hostname = Column(String)
    company = Column(String)
    technologies = Column(ARRAY(String))
    loadtime = Column(Integer)
    changes = Column(Integer)
    cloudscore = Column(Integer)
    domainlength = Column(Integer)
    eii = Column(Integer)
    forwardingcount = Column(Integer)
    htmlsize = Column(Integer)
    incominglinks = Column(Integer)
    subdomainscount = Column(Integer)
    outgoinglinks = Column(Integer)
    pagesindexed = Column(Integer)
    pages = Column(Integer)
    seo = Column(Integer)
    trustscore = Column(Integer)
    securityscore = Column(Integer)
    visitorsavg = Column(BigInteger())
    visitors = Column(BigInteger())
    grade = Column(Float)
    trustgrade = Column(String)
    trafficindex = Column(BigInteger())
    websiteage = Column(Integer)
    ecommercequality = Column(Integer)
    probability = Column(Float)
    predicted_class = Column(Integer)


class DomainApiMetadataTable(Base):
    __tablename__ = DOMAIN_API_METADATA_TABLENAME

    id = Column(BigInteger(), autoincrement=True, primary_key=True)
    company_id = Column(
        BigInteger(),
        ForeignKey(CompanyDomainDataTable.company_id, ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    fetch_datetime = Column(DateTime, default=func.now())
    total_data_fetched = Column(Integer)
    s3_domain_api_json_storage_link = Column(String, unique=True)


class WebsiteApiMetadataTable(Base):
    __tablename__ = WEBSITE_API_METADATA_TABLENAME

    id = Column(BigInteger(), autoincrement=True, primary_key=True)
    company_id = Column(
        BigInteger(),
        ForeignKey(CompanyDomainDataTable.company_id, ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    fetch_datetime = Column(DateTime, default=func.now())
    total_data_fetched = Column(Integer)
    s3_website_api_json_storage_link = Column(String, unique=True)
