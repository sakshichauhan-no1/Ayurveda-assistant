export interface Citation {
  document_id: string;
  source_name: string;
  page_number: number;
  section: string;
  text: string;
  bbox: [number, number, number, number]; // [x1, y1, x2, y2]
}

export interface StatutoryResponse {
  query: string;
  jurisdiction: "India" | "International";
  product_category: string;
  regulatory_bar: string;
  answer: string;
  citations: Citation[];
  confidence: "High" | "Insufficient evidence — human review recommended";
}

export const MOCK_WORKSPACE_DATA: Record<string, StatutoryResponse> = {
  india: {
    query: "Ashwagandha + Curcumin novel synergistic extract for anti-inflammatory application",
    jurisdiction: "India",
    product_category: "Ayurvedic Proprietary Medicine (Rule 122E / D&C Act)",
    regulatory_bar: "Section 3(p) Traditional Knowledge Bar & BDA 2024 Prior Clearance",
    answer: "Under Indian Patent Law, combinations of known Ayurvedic substances are barred under Section 3(p) of the Patents Act, 1970 as traditional knowledge unless novel biological synergism is established beyond known texts. Furthermore, under Section 6 of the Biological Diversity Act (amended 2024), accessing Indian bio-resources mandates prior National Biodiversity Authority (NBA) approval via Form 1.",
    confidence: "High",
    citations: [
      {
        document_id: "patents_act",
        source_name: "The Patents Act, 1970",
        page_number: 14,
        section: "Section 3(p)",
        text: "What are not inventions: an invention which in effect, is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components.",
        bbox: [100, 220, 500, 275]
      },
      {
        document_id: "bda_rules_2024",
        source_name: "Biological Diversity Act, 2024 ABS Guidelines",
        page_number: 8,
        section: "Section 6(1)",
        text: "No person shall apply for any intellectual property right in or outside India for any invention based on any research or information on a biological resource obtained from India without obtaining previous approval of the National Biodiversity Authority.",
        bbox: [90, 160, 510, 225]
      }
    ]
  },
  international: {
    query: "Ashwagandha formulation export to US / EU via PCT",
    jurisdiction: "International",
    product_category: "Botanical Dietary Supplement / Herbal Medicinal Product",
    regulatory_bar: "WIPO GRATK Treaty (2024) Mandatory Disclosure & US DSHEA 1994",
    answer: "For international protection via PCT, the newly adopted WIPO GRATK Treaty (2024) imposes a mandatory obligation to disclose the country of origin of Indian genetic resources and associated traditional knowledge. Formulations classified as dietary supplements in the US under DSHEA cannot claim disease treatment without IND clearance.",
    confidence: "High",
    citations: [
      {
        document_id: "wipo_gratk_2024",
        source_name: "WIPO GRATK Treaty (2024) Articles",
        page_number: 5,
        section: "Article 3 - Disclosure Requirement",
        text: "Patent applicants shall disclose the country of origin of the genetic resources and the indigenous peoples or local community that provided the traditional knowledge.",
        bbox: [95, 180, 505, 235]
      }
    ]
  }
};