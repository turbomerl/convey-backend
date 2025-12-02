"""
Shared prompt building logic and data structures for all LLM providers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence


@dataclass(frozen=True)
class SectionSpec:
    """Specification for a report section."""
    name: str
    description: str
    focus_files: Sequence[str] | None = None


@dataclass
class DocumentInput:
    """Input document for analysis."""
    name: str
    data: bytes


# Define the 16 sections for property document analysis
SECTIONS: Sequence[SectionSpec] = [
    SectionSpec(
        name="Rights Benefitting the Property",
        description="""Summarise easements or rights in favour of the property, highlighting their scope and any conditions. Be as comprehensive as possible.
                    For each right or easement extracted, output the information in the following format:
                    Title:  title ID
                    Entry Type: the entry type of the right or easement
                    Entry Text: the verbatim text of the right or easement""",
        focus_files=("",),
    ),
    SectionSpec(
        name="Rights to which the Property is subject",
        description="""List burdens or rights over the property, such as access/utility rights benefitting others, with obligations.
                    For each right or easement extracted, output the information in the following format:
                    Title:  title ID
                    Entry Type: the entry type of the right or easement
                    Entry Text: the verbatim text of the right or easement""",
        focus_files=("",),
    ),
    SectionSpec(
        name="Covenants",
        description="""Capture positive/negative covenants and indicate parties responsible for compliance.
                    For each covenant extracted, output the information in the following format:
                    Title:  title ID
                    Entry Type: the entry type of the right or easement
                    Entry Text: the verbatim text of the right or easement""",
    ),
    SectionSpec(
        name="Title Guarantee",
        description="Identify the level of title guarantee offered and any qualifications mentioned.",
    ),
    SectionSpec(
        name="Land Registry Advisory",
        description="Include title number, class of title, restrictions or notices recorded on the register.",
    ),
    SectionSpec(
        name="Lease Details",
        description="Provide parties, term, commencement, demise description, and rent review mechanics.",
        focus_files=("lease.pdf",),
    ),
    SectionSpec(
        name="Leasehold Covenants",
        description="Summarise tenant and landlord covenants, referencing repairing, alteration, and assignment clauses.",
        focus_files=("lease.pdf",),
    ),
    SectionSpec(
        name="Ground Rent",
        description="State the amount, payment frequency, escalation pattern, and review dates.",
        focus_files=("",),
    ),
    SectionSpec(
        name="Service Charge",
        description="""State the current service charge that is payable.
                    Explain how the service charge is calculated, caps, excluded items, and payment timetable.""",
        focus_files=("",),
    ),
    SectionSpec(
        name="Major Works and Reserve Fund",
        description="Identify obligations for capital works/reserve contributions and any consultation requirements.",
    ),
    SectionSpec(
        name="Administrative Charges",
        description="Outline ad-hoc fees payable to the landlord/managing agent (licence to assign, notice fees, etc.).",
    ),
    SectionSpec(
        name="Building Insurance",
        description="Describe who insures, required cover, premium recovery, and reinstatement obligations.",
    ),
    SectionSpec(
        name="Enfranchisement",
        description="Note any enfranchisement restrictions or rights concerning the property.",
    ),
    SectionSpec(
        name="Notice To Landlord",
        description="Detail notice requirements on assignment, mortgage, or subletting including fees and addresses.",
    ),
    SectionSpec(
        name="Deed of Covenant",
        description="Specify when a deed of covenant is required and its execution/registration steps.",
    ),
    SectionSpec(
        name="Airbnb/Holiday Let Advisory",
        description="State whether short-term letting is allowed, prohibited, or subject to conditions.",
    ),
]

BASE_INSTRUCTIONS = """You are a property law assistant. Analyse the uploaded PDFs
and complete every heading listed below. Cite each fact with the source file name
and page number whenever possible. Use 'No data found' only when the documents do
not address that heading at all."""


def build_text_prompt(extra_prompt: str | None = None) -> dict:
    """
    Build the text prompt with all 16 sections and optional extra guidance.

    Args:
        extra_prompt: Optional additional instructions

    Returns:
        Dictionary with type and text for the prompt
    """
    section_lines: List[str] = []
    for idx, spec in enumerate(SECTIONS, start=1):
        section_lines.append(f"{idx}. {spec.name}")
        section_lines.append(f"   Focus: {spec.description}")
        if spec.focus_files:
            files = ", ".join(spec.focus_files)
            section_lines.append(f"   Prioritise details from: {files}, but search all files")

    instructions = BASE_INSTRUCTIONS + "\n" + "\n".join(section_lines)
    if extra_prompt:
        instructions += f"\n\nAdditional guidance:\n{extra_prompt}"

    return {
        "type": "input_text",
        "text": instructions.strip(),
    }
