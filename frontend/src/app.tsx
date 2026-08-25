import {createElement, useState} from 'react';
import type {ChangeEvent, DragEvent, ReactElement} from 'react';

// Define the supported user-interface states.
type view_state = 'form' | 'loading' | 'results';

// Define the fake response shape that matches the existing analysis schema.
type analysis_result = {
    status: 'completed';
    label: string;
    overall_score: {
        value: number;
        scale: number;
        band: string;
    };
    coverage: {
        technical_skill_coverage: number;
        required_skill_coverage: number;
        preferred_skill_coverage: number;
    };
    matching_skills: string[];
    missing_required_skills: string[];
    missing_preferred_skills: string[];
    resume_evidence: string;
    job_description_evidence: string;
    recommendations: string[];
    confidence: string;
    limitations: string[];
};

// Store the product limits in one place so validation stays consistent.
const maximum_file_size = 5 * 1024 * 1024;
const minimum_job_description_length = 80;

// Return a readable file size for the upload summary.
const format_file_size = (file_size: number): string => `${(file_size / 1024 / 1024).toFixed(2)} MB`;

// Build the fake result used until the backend analysis endpoint exists.
const create_fake_result = (): analysis_result => ({
    status: 'completed',
    label: 'OptiMatch compatibility estimate',
    overall_score: {
        value: 72,
        scale: 100,
        band: 'moderate_alignment',
    },
    coverage: {
        technical_skill_coverage: 68,
        required_skill_coverage: 75,
        preferred_skill_coverage: 50,
    },
    matching_skills: ['Python', 'SQL', 'Git', 'REST APIs'],
    missing_required_skills: ['Docker'],
    missing_preferred_skills: ['Kubernetes', 'CI/CD'],
    resume_evidence: 'Python and SQL appear in the projects and technical-skills sections of the submitted resume.',
    job_description_evidence: 'The job description emphasizes Python, SQL, Docker, REST APIs, and collaborative development.',
    recommendations: [
        'Add truthful evidence showing how you used Python and SQL in a project.',
        'If you have used Docker, name the specific project and your contribution.',
        'Consider strengthening evidence for deployment or CI/CD experience.',
    ],
    confidence: 'Medium confidence because this prototype uses a simulated analysis response.',
    limitations: [
        'This result is an OptiMatch compatibility estimate, not an official ATS score.',
        'A skill not detected in the resume may still be possessed by the applicant.',
    ],
});

// Render the complete interface and manage its temporary client-side state.
const optimatch_app = (): ReactElement => {
    const [view_state, set_view_state] = useState<view_state>('form');
    const [resume_file, set_resume_file] = useState<File | null>(null);
    const [job_description, set_job_description] = useState('');
    const [error_message, set_error_message] = useState('');
    const [is_dragging, set_is_dragging] = useState(false);
    const [analysis_result, set_analysis_result] = useState<analysis_result | null>(null);

    // Validate one selected resume against the product rules.
    const validate_resume_file = (selected_file: File): string => {
        if (!selected_file.name.toLowerCase().endsWith('.pdf') || (selected_file.type && selected_file.type !== 'application/pdf')) {
            return 'Only PDF files are accepted.';
        }
        if (selected_file.size > maximum_file_size) {
            return 'Your resume is larger than the 5 MB limit.';
        }
        return '';
    };

    // Accept a file from either the file picker or the drag-and-drop area.
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

    // Handle a file selected through the native file picker.
    const handle_file_change = (event: ChangeEvent<HTMLInputElement>): void => {
        select_resume_file(event.target.files?.[0]);
    };

    // Handle a file dropped onto the upload area.
    const handle_drop = (event: DragEvent<HTMLDivElement>): void => {
        event.preventDefault();
        set_is_dragging(false);
        select_resume_file(event.dataTransfer.files[0]);
    };

    // Validate both inputs and simulate a short analysis request.
    const handle_submit = (): void => {
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
        window.setTimeout(() => {
            set_analysis_result(create_fake_result());
            set_view_state('results');
        }, 1200);
    };

    // Return the user to the temporary form without retaining the previous result.
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

// Export the completed application element for the browser entry point.
export const app = createElement(optimatch_app);

// Display the fake analysis in the same structure expected from the future backend.
const results_view = ({ analysis_result, resume_file, on_start_over }: { analysis_result: analysis_result; resume_file: File | null; on_start_over: () => void }): ReactElement => (
    <section className='results_section'>
        <div className='results_header'><div><p className='eyebrow'>Analysis complete</p><h1>Your alignment overview</h1><p className='hero_description'>{resume_file?.name} · Temporary result</p></div><button type='button' className='secondary_button plain_button' onClick={on_start_over}>Start over</button></div>
        <div className='score_card'><div className='score_ring'><strong>{analysis_result.overall_score.value}</strong><span>/ {analysis_result.overall_score.scale}</span></div><div><p className='eyebrow'>{analysis_result.label}</p><h2>Moderate alignment</h2><p className='muted_text'>Your resume shows relevant experience, with a few opportunities to strengthen evidence for this role.</p></div></div>
        <div className='metric_grid'>{createElement(metric_card, { label: 'Required skills', value: `${analysis_result.coverage.required_skill_coverage}%` })}{createElement(metric_card, { label: 'Technical skills', value: `${analysis_result.coverage.technical_skill_coverage}%` })}{createElement(metric_card, { label: 'Confidence', value: 'Medium' })}</div>
        <div className='result_grid'>{createElement(result_list, { title: 'Matching skills', items: analysis_result.matching_skills, item_class: 'match_item' })}{createElement(result_list, { title: 'Missing required skills', items: analysis_result.missing_required_skills, item_class: 'missing_item' })}{createElement(result_list, { title: 'Missing preferred skills', items: analysis_result.missing_preferred_skills, item_class: 'preferred_item' })}</div>
        <div className='evidence_card'><p className='eyebrow'>Evidence and recommendations</p><h2>What informed this estimate</h2><p><strong>Resume evidence:</strong> {analysis_result.resume_evidence}</p><p><strong>Job evidence:</strong> {analysis_result.job_description_evidence}</p><h3>Recommended next steps</h3><ul>{analysis_result.recommendations.map((recommendation) => <li key={recommendation}>{recommendation}</li>)}</ul></div>
        <div className='limitation_card'><strong>Important limitation</strong>{analysis_result.limitations.map((limitation) => <p key={limitation}>{limitation}</p>)}</div>
    </section>
);

// Render one numeric summary card without introducing a separate data model.
const metric_card = ({ label, value }: { label: string; value: string }): ReactElement => <div className='metric_card'><span>{label}</span><strong>{value}</strong></div>;

// Render one skill group with a distinct visual meaning.
const result_list = ({ title, items, item_class }: { title: string; items: string[]; item_class: string }): ReactElement => <div className='result_list'><h3>{title}</h3>{items.map((item) => <div className={`skill_item ${item_class}`} key={item}><span>{item_class === 'match_item' ? '✓' : '!'}</span>{item}</div>)}</div>;