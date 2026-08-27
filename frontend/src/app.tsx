import {createElement, useState} from 'react';
import type {ChangeEvent, DragEvent, ReactElement} from 'react';

// Define the supported user-interface states
type view_state = 'form' | 'loading' | 'results';

// Define the response shape
type analysis_result = {
    status: 'completed';
    analysis_status: 'scored' | 'no_skills_detected' | 'insufficient_evidence';
    skill_match_status: 'matched' | 'zero_match' | 'no_skills_detected' | 'insufficient_evidence';
    label: string;
    overall_score: {
        value: number | null;
        scale: number;
        band: string;
    };
    compatibility_band: {
        value: string;
        label: string;
    };
    formatting_risk: number;
    coverage: {
        technical_skill_coverage: number;
        required_skill_coverage: number;
        preferred_skill_coverage: number;
    };
    matching_skills: {skill: string}[];
    matched_required_skills: {skill: string}[];
    matched_preferred_skills: {skill: string}[];
    matched_general_skills: {skill: string}[];
    missing_required_skills: {skill: string}[];
    missing_preferred_skills: {skill: string}[];
    resume_evidence: {normalized_skill_name?: string; text_evidence?: string}[];
    job_description_evidence: {skill?: string; text_evidence?: string}[];
    formatting_risks: {issue: string; severity: string}[];
    recommendations: {skill: string; priority: string; recommended_action: string}[];
    confidence: {overall?: string};
    limitations: string[];
    detected_resume_skills: string[];
    detected_job_skills: (string | {skill: string; requirement_type?: string})[];
    extraction_coverage: {
        status: 'low' | 'available';
        detected_job_skill_count: number;
        detected_required_count: number;
        detected_preferred_count: number;
        warning: string | null;
    };
};

// Store the product limits in one place
const maximum_file_size = 5 * 1024 * 1024;
const minimum_job_description_length = 80;

// Return a readable file size for the upload summary
const format_file_size = (file_size: number): string => `${(file_size / 1024 / 1024).toFixed(2)} MB`;

// Render the complete interface and manage its temporary client-side state
const optimatch_app = (): ReactElement => {
    const [view_state, set_view_state] = useState<view_state>('form');
    const [resume_file, set_resume_file] = useState<File | null>(null);
    const [job_description, set_job_description] = useState('');
    const [error_message, set_error_message] = useState('');
    const [is_dragging, set_is_dragging] = useState(false);
    const [analysis_result, set_analysis_result] = useState<analysis_result | null>(null);

    // Validate one selected resume against the product rules
    const validate_resume_file = (selected_file: File): string => {
        if (!selected_file.name.toLowerCase().endsWith('.pdf') || (selected_file.type && selected_file.type !== 'application/pdf')) {
            return 'Only PDF files are accepted.';
        }
        if (selected_file.size > maximum_file_size) {
            return 'Your resume is larger than the 5 MB limit.';
        }
        return '';
    };

    // Accept a file from either the file picker or the drag-and-drop area
    const select_resume_file = (selected_file: File | undefined): void => {
        if (!selected_file) return;
        const validation_error = validate_resume_file(selected_file);
        set_error_message(validation_error);
        if (validation_error) {
            set_resume_file(null);
            return;
        }
        set_resume_file(selected_file);
    };

    // Handle a file selected through the native file picker
    const handle_file_change = (event: ChangeEvent<HTMLInputElement>): void => {
        select_resume_file(event.target.files?.[0]);
    };

    // Handle a file dropped onto the upload area
    const handle_drop = (event: DragEvent<HTMLDivElement>): void => {
        event.preventDefault();
        set_is_dragging(false);
        select_resume_file(event.dataTransfer.files[0]);
    };

    // Validate both inputs and send the PDF and job description to the backend
    const handle_submit = async (): Promise<void> => {
        if (!resume_file) {
            set_error_message('Please upload your resume before continuing.');
            return;
        }
        if (job_description.trim().length < minimum_job_description_length) {
            set_error_message(`Please enter at least ${minimum_job_description_length} characters in the job description.`);
            return;
        }
        set_error_message('');
        set_view_state('loading');
        const form_data = new FormData();
        form_data.append('resume', resume_file);
        form_data.append('job_description', job_description);
        try {
            // Keep the request on the Vite frontend
            const api_endpoint = `${window.location.origin}/api/analyze`;
            const response = await fetch(api_endpoint, {
                method: 'POST',
                body: form_data,
            });
            const response_text = await response.text();
            let response_data: {detail?: string; [key: string]: unknown} = {};
            if (!response_text.trim()) {
                throw new Error('The backend is not running. Start the OptiMatch API on port 8000 and try again.');
            }
            try {
                response_data = JSON.parse(response_text);
            } catch {
                throw new Error('The backend returned an invalid response.');
            }
            if (!response.ok) {
                throw new Error(response_data.detail || 'The analysis could not be completed.');
            }
            set_analysis_result(response_data as analysis_result);
            set_view_state('results');
        } catch (error) {
            set_error_message(error instanceof TypeError ? 'The backend is not running. Start the OptiMatch API on port 8000 and try again.' : error instanceof Error ? error.message : 'The analysis could not be completed.');
            set_view_state('form');
        }
    };

    // Return the user to the temporary form without retaining the previous result
    const handle_start_over = (): void => {
        set_view_state('form');
        set_resume_file(null);
        set_job_description('');
        set_analysis_result(null);
        set_error_message('');
    };

    return (
        <main className='page_shell'>
            <header className='site_header'>
              <div className='brand_mark'>Opti<span>Match</span></div>
              <div className='beta_badge'>Private beta</div>
            </header>

            {view_state === 'form' && (
                <section className='hero_section'>
                    <div className='hero_copy'>
                      <p className='eyebrow'>Resume intelligence for your next application</p>
                      <h1>Understand how your resume aligns with the role.</h1>
                      <p className='hero_description'>Upload a text-based resume PDF and paste one job description to receive a transparent compatibility estimate.</p>
                    </div>

                    <section className='analysis_card' aria-label='Resume analysis form'>
                        <div className='step_heading'><span>01</span><div><h2>Add your resume</h2><p>Text-based PDF only · Maximum 5 MB</p></div></div>
                        <div className={`upload_zone ${is_dragging ? 'upload_zone_dragging' : ''}`} onDragOver={(event) => { event.preventDefault(); set_is_dragging(true); }} onDragLeave={() => set_is_dragging(false)} onDrop={handle_drop}>
                            {resume_file ? (
                                <div className='file_summary'><div><strong>{resume_file.name}</strong><span>{format_file_size(resume_file.size)}</span></div><button type='button' className='text_button' onClick={() => set_resume_file(null)}>Remove</button></div>
                            ) : (
                                <><div className='upload_icon'>↑</div><strong>Drop your resume here</strong><span>or</span><label className='secondary_button'>Browse PDF<input type='file' accept='.pdf,application/pdf' onChange={handle_file_change} /></label></>
                            )}
                        </div>

                        <div className='step_heading'><span>02</span><div><h2>Paste the job description</h2><p>Include the complete posting for a more useful comparison</p></div></div>
                        <textarea className='job_input' value={job_description} onChange={(event) => set_job_description(event.target.value)} placeholder='Paste the job description here...' aria-label='Job description' />
                        <div className='input_footer'><span>{job_description.length} characters</span><span>Not saved</span></div>

                        {error_message && <div className='error_message' role='alert'>{error_message}</div>}
                        <button type='button' className='primary_button full_width' onClick={handle_submit}>Analyze my resume <span>→</span></button>
                        <p className='privacy_note'>Your resume and job description are processed temporarily and are not saved.</p>
                    </section>
                </section>
            )}

            {view_state === 'loading' && <section className='status_panel'><div className='loading_orbit' /><p className='eyebrow'>OptiMatch is working</p><h1>Analyzing your alignment...</h1><p>We are comparing the requirements in the job description with the evidence in your resume.</p></section>}

            {view_state === 'results' && analysis_result && createElement(results_view, { analysis_result, resume_file, on_start_over: handle_start_over })}
        </main>
    );
};

// Export the completed application element for the browser entry point
export const app = createElement(optimatch_app);

// Display the explainable result returned by the backend
const results_view = ({analysis_result, resume_file, on_start_over }: { analysis_result: analysis_result; resume_file: File | null; on_start_over: () => void }): ReactElement => (
    <section className='results_section'>
        <div className='results_header'><div><p className='eyebrow'>Analysis complete</p><h1>Your alignment overview</h1><p className='hero_description'>{resume_file?.name} · Temporary result</p></div><button type='button' className='secondary_button plain_button' onClick={on_start_over}>Start over</button></div>
        <div className='score_card'><div className='score_ring'><strong>{analysis_result.overall_score.value ?? '—'}</strong><span>{analysis_result.overall_score.value === null ? 'not scored' : `/ ${analysis_result.overall_score.scale}`}</span></div><div><p className='eyebrow'>{analysis_result.label}</p><h2>{analysis_result.compatibility_band.label}</h2><p className='muted_text'>{analysis_result.skill_match_status === 'zero_match' ? 'Skills were detected in both documents, but none matched exactly or through a configured alias.' : analysis_result.analysis_status === 'scored' ? 'This score combines required skills, technical skills, evidence alignment, and formatting quality.' : 'No reliable compatibility score was calculated because the available skill evidence was incomplete.'}</p></div></div>
        <div className='metric_grid'>{createElement(metric_card, { label: 'Required skills', value: `${analysis_result.coverage.required_skill_coverage}%` })}{createElement(metric_card, { label: 'Technical skills', value: `${analysis_result.coverage.technical_skill_coverage}%` })}{createElement(metric_card, { label: 'Formatting risk', value: `${analysis_result.formatting_risk}%` })}</div>
        <div className='result_grid'>{createElement(result_list, { title: 'Matched required skills', items: analysis_result.matched_required_skills.map((skill) => skill.skill), item_class: 'match_item' })}{createElement(result_list, { title: 'Missing required skills', items: analysis_result.missing_required_skills.map((skill) => skill.skill), item_class: 'missing_item' })}{createElement(result_list, { title: 'Matched preferred skills', items: analysis_result.matched_preferred_skills.map((skill) => skill.skill), item_class: 'preferred_item' })}</div>
        <div className='result_grid'>{createElement(result_list, { title: 'Matched general skills', items: analysis_result.matched_general_skills.map((skill) => skill.skill), item_class: 'match_item' })}{createElement(result_list, { title: 'Missing preferred skills', items: analysis_result.missing_preferred_skills.map((skill) => skill.skill), item_class: 'preferred_item' })}{createElement(result_list, { title: 'All matched skills', items: analysis_result.matching_skills.map((skill) => skill.skill), item_class: 'match_item' })}</div>
        <div className='evidence_card'><p className='eyebrow'>Detected skills</p><h2>What OptiMatch extracted</h2><p><strong>Resume:</strong> {analysis_result.detected_resume_skills.length ? analysis_result.detected_resume_skills.join(', ') : 'No skills detected'}</p><p><strong>Job description:</strong> {analysis_result.detected_job_skills.length ? analysis_result.detected_job_skills.map((skill) => typeof skill === 'string' ? skill : skill.skill).join(', ') : 'No skills detected'}</p></div>
        <div className='evidence_card'><p className='eyebrow'>Extraction coverage</p><h2>How much of the job description was recognized</h2><p><strong>Detected job skills:</strong> {analysis_result.extraction_coverage.detected_job_skill_count}</p><p><strong>Required requirements:</strong> {analysis_result.extraction_coverage.detected_required_count}</p><p><strong>Preferred requirements:</strong> {analysis_result.extraction_coverage.detected_preferred_count}</p>{analysis_result.extraction_coverage.warning && <p className='muted_text'>{analysis_result.extraction_coverage.warning}</p>}</div>
        <div className='evidence_card'><p className='eyebrow'>Resume evidence</p><h2>Where matching skills appear</h2><ul>{analysis_result.resume_evidence.map((evidence, index) => <li key={`${evidence.normalized_skill_name}-${index}`}><strong>{evidence.normalized_skill_name}:</strong> {evidence.text_evidence}</li>)}</ul><h3>Learning recommendations</h3><ul>{analysis_result.recommendations.map((recommendation) => <li key={recommendation.skill}><strong>{recommendation.priority} priority — {recommendation.skill}:</strong> {recommendation.recommended_action}</li>)}</ul></div>
        <div className='evidence_card'><p className='eyebrow'>Formatting checks</p><h2>Potential ATS-readability issues</h2>{analysis_result.formatting_risks.length ? <ul>{analysis_result.formatting_risks.map((risk) => <li key={risk.issue}>{risk.issue}</li>)}</ul> : <p className='muted_text'>No formatting risks were detected by the available checks.</p>}</div>
        <div className='limitation_card'><strong>Important limitation</strong>{analysis_result.limitations.map((limitation) => <p key={limitation}>{limitation}</p>)}</div>
    </section>
);

// Render one numeric summary card without introducing a separate data model
const metric_card = ({ label, value }: { label: string; value: string }): ReactElement => <div className='metric_card'><span>{label}</span><strong>{value}</strong></div>;

// Render one skill group with a distinct visual meaning
const result_list = ({ title, items, item_class }: { title: string; items: string[]; item_class: string }): ReactElement => <div className='result_list'><h3>{title}</h3>{items.map((item) => <div className={`skill_item ${item_class}`} key={item}><span>{item_class === 'match_item' ? '✓' : '!'}</span>{item}</div>)}</div>;
