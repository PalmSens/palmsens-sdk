function [busy, comms] = MultiChannelMeasurementLoopHelper(comms)
    % Wait for multiple instruments to finish their measurements.
    %
    % Parameters:
    %   comms: List of channels
    %
    % Returns:
    %   busy (bool): Return true if any channel is busy
    %   comms (int): List of channels

    n = length(comms);
    activeChannels = ones(1, n);

    for i = 1:n
        if activeChannels(i) && ~comms(i).m.inMeasurement
            if comms(i).queueIndex <= length(comms(i).queue)
                % start measurement if channel is idle and queue is not complete
                comms(i).m.New(comms(i).queue(comms(i).queueIndex).method);
                comms(i).queueIndex = comms(i).queueIndex + 1;
            else
                % set channel to inactive when channel is idle and queue is
                % complete
                activeChannels(i) = false;
            end
        end
    end

    busy = max(activeChannels);

end
