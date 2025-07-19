function createExperienceFields() {
    const wrapper = document.createElement('div');
    wrapper.className = 'experience-item space-y-2';
    wrapper.innerHTML = `
        <input type="text" placeholder="Period" class="period w-full px-4 py-2 border border-gray-300 rounded-lg">
        <input type="text" placeholder="Title" class="title w-full px-4 py-2 border border-gray-300 rounded-lg">
        <input type="text" placeholder="Company" class="company w-full px-4 py-2 border border-gray-300 rounded-lg">
        <input type="text" placeholder="Location" class="location w-full px-4 py-2 border border-gray-300 rounded-lg">
        <textarea placeholder="Description or AI notes" class="description w-full px-4 py-2 border border-gray-300 rounded-lg"></textarea>
        <button type="button" class="ai-generate bg-primary text-white px-4 py-2 rounded" data-field="job experience description" data-target="description" data-remaining="3">AI (<span class="counter">3</span>)</button>
    `;
    return wrapper;
}

document.getElementById('addExperience').addEventListener('click', () => {
    document.getElementById('experienceContainer').appendChild(createExperienceFields());
});

function createEducationFields() {
    const wrapper = document.createElement('div');
    wrapper.className = 'education-item space-y-2';
    wrapper.innerHTML = `
        <input type="text" placeholder="Period" class="period w-full px-4 py-2 border border-gray-300 rounded-lg">
        <input type="text" placeholder="Degree" class="degree w-full px-4 py-2 border border-gray-300 rounded-lg">
        <input type="text" placeholder="Institution" class="institution w-full px-4 py-2 border border-gray-300 rounded-lg">
        <input type="text" placeholder="Field of Study" class="field w-full px-4 py-2 border border-gray-300 rounded-lg">
        <textarea placeholder="Description or AI notes" class="description w-full px-4 py-2 border border-gray-300 rounded-lg"></textarea>
        <button type="button" class="ai-generate bg-primary text-white px-4 py-2 rounded" data-field="educational experience description" data-target="description" data-remaining="3">AI (<span class="counter">3</span>)</button>
    `;
    return wrapper;
}

document.getElementById('addEducation').addEventListener('click', () => {
    document.getElementById('educationContainer').appendChild(createEducationFields());
});

function createLanguageFields() {
    const wrapper = document.createElement('div');
    wrapper.className = 'language-item space-y-2';
    wrapper.innerHTML = `
        <input type="text" placeholder="Language" class="language w-full px-4 py-2 border border-gray-300 rounded-lg">
        <input type="text" placeholder="Level" class="level w-full px-4 py-2 border border-gray-300 rounded-lg">
    `;
    return wrapper;
}

document.getElementById('addLanguage').addEventListener('click', () => {
    document.getElementById('languageContainer').appendChild(createLanguageFields());
});

document.addEventListener('click', async (e) => {
    if (e.target.classList.contains('ai-generate')) {
        const btn = e.target;
        let remaining = parseInt(btn.dataset.remaining, 10);
        if (remaining <= 0) return;
        const fieldName = btn.dataset.field;
        let target;
        if (btn.dataset.target === 'summary' || btn.dataset.target === 'skills') {
            target = document.getElementById(btn.dataset.target);
        } else {
            target = btn.parentElement.querySelector('.' + btn.dataset.target);
        }
        const instructions = target.value;
        const response = await fetch('/generate-field', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ field_name: fieldName, instructions })
        });
        if (response.ok) {
            const data = await response.json();
            target.value = data.text;
            remaining -= 1;
            btn.dataset.remaining = remaining;
            btn.querySelector('.counter').textContent = remaining;
        } else {
            alert('Error generating text');
        }
    }
});

const steps = Array.from(document.querySelectorAll('.form-step'));
let currentStep = 0;
const nextButtons = document.querySelectorAll('.next-step');
const prevButtons = document.querySelectorAll('.prev-step');
const stepLinks = document.querySelectorAll('.step-link');

function updateStepNav() {
    stepLinks.forEach((link, idx) => {
        const active = idx === currentStep;
        link.classList.toggle('bg-primary', active);
        link.classList.toggle('text-white', active);
        link.classList.toggle('bg-gray-200', !active);
        link.classList.toggle('text-gray-700', !active);
    });
}

function showStep(i) {
    steps.forEach((step, idx) => {
        step.classList.toggle('hidden', idx !== i);
    });
    updateStepNav();
}

nextButtons.forEach(btn => btn.addEventListener('click', () => {
    if (currentStep < steps.length - 1) {
        currentStep++;
        showStep(currentStep);
    }
}));

prevButtons.forEach(btn => btn.addEventListener('click', () => {
    if (currentStep > 0) {
        currentStep--;
        showStep(currentStep);
    }
}));

stepLinks.forEach(link => link.addEventListener('click', () => {
    const step = parseInt(link.dataset.step, 10);
    if (!isNaN(step)) {
        currentStep = step;
        showStep(currentStep);
    }
}));

showStep(currentStep);

function gatherData() {
    const experiences = [];
    document.querySelectorAll('#experienceContainer .experience-item').forEach(item => {
        experiences.push({
            period: item.querySelector('.period').value,
            title: item.querySelector('.title').value,
            company: item.querySelector('.company').value,
            location: item.querySelector('.location').value,
            description: item.querySelector('.description').value
        });
    });

    const education = [];
    document.querySelectorAll('#educationContainer .education-item').forEach(item => {
        education.push({
            period: item.querySelector('.period').value,
            degree: item.querySelector('.degree').value,
            institution: item.querySelector('.institution').value,
            field_of_study: item.querySelector('.field').value,
            description: item.querySelector('.description').value
        });
    });

    const languages = [];
    document.querySelectorAll('#languageContainer .language-item').forEach(item => {
        const lang = item.querySelector('.language').value;
        const level = item.querySelector('.level').value;
        if (lang) languages.push(`${lang} (${level})`);
    });

    return {
        name: document.getElementById('name').value,
        location: document.getElementById('location').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        linkedin: document.getElementById('linkedin').value,
        github: document.getElementById('github').value,
        website: document.getElementById('website').value,
        summary: document.getElementById('summary').value,
        skills: document.getElementById('skills').value,
        experiences,
        education,
        languages
    };
}

document.getElementById('builderForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = gatherData();
    const response = await fetch('/create-resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'resume.pdf';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } else {
        alert('Error generating resume');
    }
});
