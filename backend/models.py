from pydantic import BaseModel
from typing import Optional, List


class CVHeader(BaseModel):
    nama: str = ""
    lokasi: str = ""
    email: str = ""
    telepon: str = ""
    linkedin_atau_portfolio: str = ""


class CVPendidikan(BaseModel):
    institusi: str = ""
    lokasi: str = ""
    periode: str = ""
    jurusan_gelar: str = ""
    ipk: str = ""
    skripsi: str = ""
    pelatihan: List[str] = []


class CVPengalaman(BaseModel):
    organisasi: str = ""
    lokasi: str = ""
    periode: str = ""
    posisi: str = ""
    poin: List[str] = []


class CVLeadership(BaseModel):
    organisasi: str = ""
    lokasi: str = ""
    periode: str = ""
    peran: str = ""
    poin: List[str] = []


class CVKemampuan(BaseModel):
    hard_skills: List[str] = []
    tools_software: List[str] = []
    bahasa: List[str] = []


class CVData(BaseModel):
    bidang: str = "default"
    header: CVHeader = CVHeader()
    ringkasan_profesional: str = ""
    pendidikan: List[CVPendidikan] = []
    pengalaman: List[CVPengalaman] = []
    sertifikasi_pencapaian: List[str] = []
    leadership_activities: List[CVLeadership] = []
    kemampuan: CVKemampuan = CVKemampuan()
    notes: str = ""
