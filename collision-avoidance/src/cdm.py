from dataclasses import dataclass, field
from typing import Optional
import xml.etree.ElementTree as ET
from pathlib import Path


@dataclass
class RelativeStateVector:
    relative_position_r: float
    relative_position_t: float
    relative_position_n: float
    relative_velocity_r: float
    relative_velocity_t: float
    relative_velocity_n: float


@dataclass
class CovarianceMatrix:
    cr_r: float
    ct_r: float
    ct_t: float
    cn_r: float
    cn_t: float
    cn_n: float
    crdot_r: float
    crdot_t: float
    crdot_n: float
    crdot_rdot: float
    ctdot_r: float
    ctdot_t: float
    ctdot_n: float
    ctdot_rdot: float
    ctdot_tdot: float
    cndot_r: float
    cndot_t: float
    cndot_n: float
    cndot_rdot: float
    cndot_tdot: float
    cndot_ndot: float


@dataclass
class StateVector:
    x: float
    y: float
    z: float
    x_dot: float
    y_dot: float
    z_dot: float


@dataclass
class Metadata:
    object: str
    object_designator: str
    catalog_name: str
    object_name: str
    international_designator: str
    object_type: str
    ephemeris_name: str
    covariance_method: str
    maneuverable: str
    ref_frame: str
    gravity_model: Optional[str] = None
    atmospheric_model: Optional[str] = None
    n_body_perturbations: Optional[str] = None
    solar_rad_pressure: Optional[str] = None
    earth_tides: Optional[str] = None


@dataclass
class AdditionalParameters:
    comment: str
    area_pc: float
    cr_area_over_mass: Optional[float] = None


@dataclass
class SegmentData:
    od_parameters: Optional[dict] = field(default_factory=dict)
    additional_parameters: Optional[AdditionalParameters] = None
    state_vector: Optional[StateVector] = None
    covariance_matrix: Optional[CovarianceMatrix] = None


@dataclass
class Segment:
    metadata: Metadata
    data: SegmentData


@dataclass
class RelativeMetadataData:
    tca: str
    miss_distance: float
    relative_speed: float
    relative_state_vector: RelativeStateVector
    start_screen_period: str
    stop_screen_period: str
    screen_volume_frame: str
    screen_volume_shape: str
    screen_volume_x: float
    screen_volume_y: float
    screen_volume_z: float
    screen_entry_time: str
    screen_exit_time: str


@dataclass
class Header:
    comment: list[str]
    creation_date: str
    originator: str
    message_for: str
    message_id: str


@dataclass
class CDM:
    header: Header
    relative_metadata_data: RelativeMetadataData
    segments: list[Segment]


def parse_relative_state_vector(element: ET.Element) -> RelativeStateVector:
    return RelativeStateVector(
        relative_position_r=float(element.find("RELATIVE_POSITION_R").text),
        relative_position_t=float(element.find("RELATIVE_POSITION_T").text),
        relative_position_n=float(element.find("RELATIVE_POSITION_N").text),
        relative_velocity_r=float(element.find("RELATIVE_VELOCITY_R").text),
        relative_velocity_t=float(element.find("RELATIVE_VELOCITY_T").text),
        relative_velocity_n=float(element.find("RELATIVE_VELOCITY_N").text),
    )


def parse_covariance_matrix(element: ET.Element) -> CovarianceMatrix:
    return CovarianceMatrix(**{tag.tag.lower(): float(tag.text) for tag in element})


def parse_state_vector(element: ET.Element) -> StateVector:
    return StateVector(
        x=float(element.find("X").text),
        y=float(element.find("Y").text),
        z=float(element.find("Z").text),
        x_dot=float(element.find("X_DOT").text),
        y_dot=float(element.find("Y_DOT").text),
        z_dot=float(element.find("Z_DOT").text),
    )


def parse_metadata(element: ET.Element) -> Metadata:
    return Metadata(**{child.tag.lower(): child.text for child in element})


def parse_additional_parameters(element: ET.Element) -> AdditionalParameters:
    return AdditionalParameters(
        **{child.tag.lower(): float(child.text) if child.text.isdigit() else child.text for child in element})


def parse_segment_data(element: ET.Element) -> SegmentData:
    state_vector = element.find("STATE_VECTOR")
    covariance_matrix = element.find("COVARIANCE_MATRIX")
    additional_parameters = element.find("ADDITIONAL_PARAMETERS")

    return SegmentData(
        state_vector=parse_state_vector(state_vector) if state_vector is not None else None,
        covariance_matrix=parse_covariance_matrix(covariance_matrix) if covariance_matrix is not None else None,
        additional_parameters=parse_additional_parameters(
            additional_parameters) if additional_parameters is not None else None,
    )


def parse_segment(element: ET.Element) -> Segment:
    metadata = parse_metadata(element.find("METADATA"))
    data = parse_segment_data(element.find("DATA"))
    return Segment(metadata=metadata, data=data)


def parse_relative_metadata_data(element: ET.Element) -> RelativeMetadataData:
    relative_state_vector = parse_relative_state_vector(element.find("RELATIVE_STATE_VECTOR"))
    return RelativeMetadataData(
        tca=element.find("TCA").text,
        miss_distance=float(element.find("MISS_DISTANCE").text),
        relative_speed=float(element.find("RELATIVE_SPEED").text),
        relative_state_vector=relative_state_vector,
        start_screen_period=element.find("START_SCREEN_PERIOD").text,
        stop_screen_period=element.find("STOP_SCREEN_PERIOD").text,
        screen_volume_frame=element.find("SCREEN_VOLUME_FRAME").text,
        screen_volume_shape=element.find("SCREEN_VOLUME_SHAPE").text,
        screen_volume_x=float(element.find("SCREEN_VOLUME_X").text),
        screen_volume_y=float(element.find("SCREEN_VOLUME_Y").text),
        screen_volume_z=float(element.find("SCREEN_VOLUME_Z").text),
        screen_entry_time=element.find("SCREEN_ENTRY_TIME").text,
        screen_exit_time=element.find("SCREEN_EXIT_TIME").text,
    )


def parse_header(element: ET.Element) -> Header:
    comments = [comment.text for comment in element.findall("COMMENT")]
    return Header(
        comment=comments,
        creation_date=element.find("CREATION_DATE").text,
        originator=element.find("ORIGINATOR").text,
        message_for=element.find("MESSAGE_FOR").text,
        message_id=element.find("MESSAGE_ID").text,
    )


def parse_cdm(xml_file: Path) -> CDM:
    tree = ET.parse(xml_file)
    root = tree.getroot()

    header = parse_header(root.find("header"))
    relative_metadata_data = parse_relative_metadata_data(root.find("RELATIVE_METADATA_DATA"))
    segments = [parse_segment(seg) for seg in root.findall("SEGMENT")]

    return CDM(
        header=header,
        relative_metadata_data=relative_metadata_data,
        segments=segments,
    )
