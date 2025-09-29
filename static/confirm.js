// Dynamic form management for CV confirmation page

// Add skill function
function addSkill() {
    const skillsList = document.getElementById('skills-list');
    const newSkillItem = document.createElement('div');
    newSkillItem.className = 'list-item';
    newSkillItem.innerHTML = `
        <input type="text" name="skills" placeholder="Enter skill">
        <button type="button" class="remove-btn" onclick="removeItem(this)">×</button>
    `;
    skillsList.appendChild(newSkillItem);
}

// Add certification function
function addCertification() {
    const certsList = document.getElementById('certifications-list');
    const newCertItem = document.createElement('div');
    newCertItem.className = 'list-item';
    newCertItem.innerHTML = `
        <input type="text" name="certifications" placeholder="Enter certification">
        <button type="button" class="remove-btn" onclick="removeItem(this)">×</button>
    `;
    certsList.appendChild(newCertItem);
}

// Remove item from dynamic lists
function removeItem(button) {
    const listItem = button.parentElement;
    const parentList = listItem.parentElement;

    // Don't remove if it's the only item
    if (parentList.children.length > 1) {
        listItem.remove();
    } else {
        // Clear the input instead
        const input = listItem.querySelector('input');
        input.value = '';
    }
}

// Add experience function
function addExperience() {
    const experienceList = document.getElementById('experience-list');
    const newExpItem = document.createElement('div');
    newExpItem.className = 'experience-item';
    newExpItem.innerHTML = `
        <div class="form-grid">
            <div class="form-group">
                <label>Job Title</label>
                <input type="text" name="exp_title">
            </div>
            <div class="form-group">
                <label>Company</label>
                <input type="text" name="exp_company">
            </div>
            <div class="form-group">
                <label>Start Date</label>
                <input type="text" name="exp_start" placeholder="MM/YYYY">
            </div>
            <div class="form-group">
                <label>End Date</label>
                <input type="text" name="exp_end" placeholder="MM/YYYY or Present">
            </div>
        </div>
        <div class="form-group full-width">
            <label>Key Responsibilities</label>
            <textarea name="exp_responsibilities" rows="3"></textarea>
        </div>
        <button type="button" class="remove-btn" onclick="removeExperience(this)">Remove Experience</button>
    `;
    experienceList.appendChild(newExpItem);
}

// Remove experience function
function removeExperience(button) {
    const experienceItem = button.parentElement;
    const parentList = experienceItem.parentElement;

    // Don't remove if it's the only item
    if (parentList.children.length > 1) {
        experienceItem.remove();
    } else {
        // Clear all inputs instead
        const inputs = experienceItem.querySelectorAll('input, textarea');
        inputs.forEach(input => input.value = '');
    }
}

// Add education function
function addEducation() {
    const educationList = document.getElementById('education-list');
    const newEduItem = document.createElement('div');
    newEduItem.className = 'education-item';
    newEduItem.innerHTML = `
        <div class="form-grid">
            <div class="form-group">
                <label>Degree</label>
                <input type="text" name="edu_degree">
            </div>
            <div class="form-group">
                <label>Institution</label>
                <input type="text" name="edu_institution">
            </div>
            <div class="form-group">
                <label>Graduation Date</label>
                <input type="text" name="edu_date" placeholder="MM/YYYY">
            </div>
            <div class="form-group">
                <label>GPA (Optional)</label>
                <input type="text" name="edu_gpa">
            </div>
        </div>
        <button type="button" class="remove-btn" onclick="removeEducation(this)">Remove Education</button>
    `;
    educationList.appendChild(newEduItem);
}

// Remove education function
function removeEducation(button) {
    const educationItem = button.parentElement;
    const parentList = educationItem.parentElement;

    // Don't remove if it's the only item
    if (parentList.children.length > 1) {
        educationItem.remove();
    } else {
        // Clear all inputs instead
        const inputs = educationItem.querySelectorAll('input');
        inputs.forEach(input => input.value = '');
    }
}

// Form validation and submission
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.confirm-form');

    form.addEventListener('submit', function(e) {
        // Check if at least name is filled
        const name = document.getElementById('name').value.trim();
        if (!name) {
            e.preventDefault();
            alert('Please enter your name before proceeding.');
            document.getElementById('name').focus();
            return false;
        }

        // Check if at least one skill is provided
        const skills = form.querySelectorAll('input[name="skills"]');
        let hasSkill = false;
        skills.forEach(input => {
            if (input.value.trim()) {
                hasSkill = true;
            }
        });

        if (!hasSkill) {
            e.preventDefault();
            alert('Please enter at least one skill before proceeding.');
            return false;
        }

        // Show loading state
        const submitBtn = form.querySelector('.submit-btn');
        const originalContent = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span>Processing... Please wait</span>';
        submitBtn.disabled = true;

        // Re-enable button after 5 seconds if form hasn't been submitted
        setTimeout(() => {
            if (submitBtn.disabled) {
                submitBtn.innerHTML = originalContent;
                submitBtn.disabled = false;
            }
        }, 5000);
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Format date inputs
    const dateInputs = document.querySelectorAll('input[name*="_start"], input[name*="_end"], input[name*="_date"]');
    dateInputs.forEach(input => {
        input.addEventListener('blur', function() {
            let value = this.value.trim();
            if (value && value.toLowerCase() !== 'present') {
                // Try to format as MM/YYYY
                if (/^\d{1,2}\/?\d{4}$/.test(value)) {
                    if (!value.includes('/')) {
                        // Assume format is MMYYYY or MYYYY
                        if (value.length === 5) {
                            value = value.substring(0, 1) + '/' + value.substring(1);
                        } else if (value.length === 6) {
                            value = value.substring(0, 2) + '/' + value.substring(2);
                        }
                    }
                    this.value = value;
                }
            }
        });
    });
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        document.querySelector('.confirm-form').submit();
    }
});