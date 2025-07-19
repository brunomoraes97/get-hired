function createExperienceFields() {
    const wrapper = document.createElement('div');
    wrapper.className = 'experience-item space-y-2';
    wrapper.innerHTML = `
        <input type="text" placeholder="Period" class="period w-full px-4 py-2 border border-gray-300 rounded-lg">
        <input type="text" placeholder="Title" class="title w-full px-4 py-2 border border-gray-300 rounded-lg">
        <input type="text" placeholder="Company" class="company w-full px-4 py-2 border border-gray-300 rounded-lg">
        <input type="text" placeholder="Location" class="location w-full px-4 py-2 border border-gray-300 rounded-lg">
        <textarea placeholder="Description or AI notes" class="description w-full px-4 py-2 border border-gray-300 rounded-lg"></textarea>
        <label class="inline-flex items-center"><input type="checkbox" class="use-ai mr-2"> Use AI</label>
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
        <label class="inline-flex items-center"><input type="checkbox" class="use-ai mr-2"> Use AI</label>
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

function gatherData() {
    const experiences = [];
    document.querySelectorAll('#experienceContainer .experience-item').forEach(item => {
        experiences.push({
            period: item.querySelector('.period').value,
            title: item.querySelector('.title').value,
            company: item.querySelector('.company').value,
            location: item.querySelector('.location').value,
            description: item.querySelector('.description').value,
            use_ai: item.querySelector('.use-ai').checked,
        });
    });

    const education = [];
    document.querySelectorAll('#educationContainer .education-item').forEach(item => {
        education.push({
            period: item.querySelector('.period').value,
            degree: item.querySelector('.degree').value,
            institution: item.querySelector('.institution').value,
            field_of_study: item.querySelector('.field').value,
            description: item.querySelector('.description').value,
            use_ai: item.querySelector('.use-ai').checked,
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
        summary: document.getElementById('summary').value,
        use_ai_summary: document.getElementById('summary_ai').checked,
        skills: document.getElementById('skills').value,
        use_ai_skills: document.getElementById('skills_ai').checked,
        experiences: experiences,
        education: education,
        languages: languages
    };
}

document.getElementById('builderForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = gatherData();
    const response = await fetch('/create-resume', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
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

let aiCount = 0;
const generateBtn = document.getElementById('generateBtn');
if (generateBtn) {
    generateBtn.addEventListener('click', () => {
        aiCount += 1;
        generateBtn.textContent = generateBtn.textContent.replace(/\(.*\)/, `(${aiCount})`);
    });
}

